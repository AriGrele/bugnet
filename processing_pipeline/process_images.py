import argparse
import cv2
import os
import math
import time
import torch
import shutil
import warnings
import json
import yaml
import random
import re
import wand.image
import sys
import numpy as np

from uniplot import plot_to_string                                              #plotting in terminal
from exif    import Image

sys.path.append("..")                                                           #to load classes from higher dir. Silly, but makes certain aspects of the code easier down the line than other package based methods

from utilities.bugnet    import Bugnet
from utilities.functions import area, bb_iou, reorder

def parse_opt():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--images',       type=str,   default='images',               help='image folder')
    parser.add_argument('--yolo_weights', type=str,   default='',                     help='path to localizer model file')
    parser.add_argument('--enet_weights', type=str,   default='',                     help='path to classifier model file')
    parser.add_argument('--dst',          type=str,   default='output',               help='destination folder for data')
    parser.add_argument('--split_n',      type=tuple, default=(1,1),                  help='x,y splits for input frame')
    parser.add_argument('--resolution',   type=int,   default=4576,                   help='resolution for yolo model')
    parser.add_argument('--classifier',   type=str,   default='enet',                 help='set to "yolo" to use species level yolo classifier')
    parser.add_argument('--conf',         type=float, default=0.25,                   help='YOLO confidence threshold')
    parser.add_argument('--iou',          type=float, default=0.45,                   help='YOLO iou threshold')
    parser.add_argument('--filter',       type=str,   default=None,                   help='binary filter path')
    parser.add_argument('--enet_res',     type=int,   default=128,                    help='resolution for efficientnet model')
    
    parser.add_argument('--show_box',     action='store_true',                        help='shows bounding boxes in debug images')    
    parser.add_argument('--subfolders',   action='store_true',                        help='use an image folder for each output class?')    
    parser.add_argument('--crop',         action='store_true',                        help='classify, or crop and classify?')    
    parser.add_argument('--just_big',     action='store_true',                        help='only the largest pass for localizing insects')    
    parser.add_argument('--just_small',   action='store_true',                        help='only the smallest pass for localizing insects')    
    parser.add_argument('--static',       action='store_true',                        help='cluster insects across frames')  
    parser.add_argument('--resize',       action='store_true',                        help='resize the input image to the model resolution')       

    return(parser.parse_args())

def progress(text,percent,char='=',length=50):                                  #progress bar
    print(f'{text} |{math.floor(percent*length)*char}{math.ceil((1-percent)*length)*" "}| {round(percent*100,2)}%',end='     \r')
    if percent>=1:print()

def read_yaml(file):                                                            #safeload data from yaml file
    with open(file,"r") as d:
        try:return(yaml.safe_load(d))
        except Exception as e:print(e)

def main(opt):
    opt.dst=os.path.abspath(opt.dst)                                            #convert dst path to absolute path, makes some aspects of saving data easier
    
    if not os.path.exists(opt.dst):
        for new in ['images/good','images/bad','boxes','misformated']:          #good images, bad images, debug boxes, files which threw errors (typically non images or incorrectly formatted images)
            os.makedirs(f'{opt.dst}/{new}',exist_ok=True)

    opt.sizes=[opt.just_big,opt.just_small]                                     #for using only low/high res passes

    vision = Bugnet(opt)                                                        #new class for processing images

    model_data = read_yaml('model.yaml')                                        #read in class counts and names for output

    with open(f'{opt.dst}/names.txt','w') as names:
        names.write('\n'.join([name for group in vision.enet.groups for name in group]))

    with open(f'{opt.dst}/morphospace.txt','w') as out:
        out.write('')

    with open(f'{opt.dst}/coords.txt','w') as out:
        out.write('')
            
    files=[os.path.join(dp, f) for dp,_,fn in os.walk(opt.images) for f in fn]  #pull all files from all folders and subfolders in input
    
    previous_layer={}                                                           #tracking dicts and lists for outputs
    clusters={}
    output_map={}
    max_id=0

    families=[]
    taxacounts=[[],[],[],[]]
    tracker   =[[],[],[],[]]

    def tree(pred,names,n):                                                     #tree function for applying conditional probabilites across taxonomic levels. 
        preds=torch.split(pred,n,1)
        prev=''

        out=[]
        for i,p in enumerate(preds):
            use=torch.tensor([(prev in x)+0 for x in names[i]]).to(vision.device)
            use=torch.mul(use,p)

            new=names[i][torch.argmax(use)]
            if not prev in new or torch.max(use)<=0.5:
                new='unknown'

            out.append(new)
            prev=new

        return(out)

    t0=time.time()                                                              #for tracking fps
    
    for index,file in enumerate(files):
        try:
            t1=time.time()
            
            subfolder=file.replace('\\','/').split('/')[-2]
        
            if not '.jpg' in file.lower() or '.jpeg' in file.lower(): continue  #currently set to only jpeg/jpg images - can handle most image types if needs be. 

            vision.grab_insects(file.replace('\\','/'))                         #localize insects in input frame

            if opt.crop:                                                        #crop out insects for classification
                boxes=[(int(b[0]),int(b[1]),int(b[2]),int(b[3])) for b in vision.boxes]
                confs=[b[4] for b in vision.boxes]
            else:
                boxes=[[.5,.5,1,1]]                                             # if no cropping, entire image is classified
                confs=[1]

            for box in boxes:                                                   #match bounding boxes in current frame to previous 
                current_layer={}
                for previous in previous_layer:
                    
                    iou=bb_iou(box,previous)
                    current_layer[iou]=reorder(previous)

                if previous_layer=={}:
                    best=0
                else:
                    best=max(list(current_layer)+[0])
                    
                if best>.6:                                                     #iou >60% for match across frames
                    new=current_layer[best]
                    if not new in clusters:
                        clusters[reorder(box)]=max_id
                        max_id+=1
                    else:
                        clusters[reorder(box)]=clusters[new]
                        if new!=reorder(box):
                            del clusters[new]
                else:
                    clusters[reorder(box)]=max_id
                    max_id+=1

            previous_layer = boxes                                              #save boxes for use in next frame

            morphotext=[]                                                       #output container for morphospecies data
            
            with open(f'{opt.dst}/data.txt','a') as out:
                if len(boxes)>0 and not vision.prediction is None:              #if there are insects in the frame
                    objects=torch.split(vision.prediction,1,0)
                    morphos=torch.split(vision.morphospace,1,0)
                    
                    for i,obj in enumerate(objects):

                        if not reorder(boxes[i]) in clusters.keys():            #define a cluster id based on previous frame matching and current max id
                            cluster_id=-1
                        else:
                            cluster_id=clusters[reorder(boxes[i])]

                        if not opt.static:                                      #if we don't care about clusters, unique id for each crop
                            cluster_id=f'{index}-{i}'

                        taxa=tree(obj,model_data['names'],model_data['n'])      #apply conditional probabilities 

                        output_taxon=[x for x in taxa if x!='unknown']          #first pass taxon guess. This does not take averages across multiple images of same individual, which can be done in postprocessing
                        if len(output_taxon)==0:
                            output_taxon=['unknown']
                            
                        for j,t in enumerate(taxa):
                            if t!='unknown':
                                taxacounts[j].append(t)
                        
                        if opt.filter is None:                                  #if no filter, all images are good
                            use='good'
                        elif torch.argmax(vision.filtered[i])==1:               #otherwise store images in good/bad folder based on filter output
                            use='good'
                        else:
                            output_taxon=['unknown']                            #do not apply a taxon name to bad images
                            use='bad'
                
                        filetext=''
                        if opt.subfolders:                                      #for storing classes in their own folders
                            for file in output_taxon:
                                filetext+=file
                                if not os.path.exists(filetext):
                                    os.makedirs(f'{opt.dst}/images/{use}/{filetext}',exist_ok=True)
                                filetext+='/'

                        if filetext=='/':
                            filetext=''

                        ##store latent space data, predictions, and image for each cropped insect
                        morphotext.append(f'{cluster_id}_{output_taxon[-1]}_{file.replace("\\","/").replace(" ",".-.")}/{vision.file_name.replace(" ",".-.")}.{index}_{i} {" ".join([str(x) for x in torch.squeeze(morphos[i]).tolist()])}')
                        
                        out.write(f'{cluster_id}_{output_taxon[-1]}_{file.replace("\\","/").replace(" ",".-.")}/{vision.file_name.replace(" ",".-.")}.{index}_{i} {" ".join([str(x) for x in torch.squeeze(obj).tolist()])}\n')
                        cv2.imwrite(f'{opt.dst}/images/{use}/{filetext}{cluster_id}_{output_taxon[-1]}_{vision.file_name}.{index}_{i}.jpg',vision.insects[i][0])

            with open(f'{opt.dst}/morphospace.txt','a') as out:                 #save latent space data
                out.write('\n'.join(morphotext)+'\n')

            with open(f'{opt.dst}/coords.txt','a') as out:                      #save bounding box data
                for i,box in enumerate(boxes):
                    out.write(f'{file.replace("\\","/").replace(" ",".-.")} {vision.file_name.replace(" ",".-.")} '+' '.join([str(x) for x in box])+' '+str(confs[i].item())+' '+str(vision.filtered[i][1].item())+'\n')
                    
                          
            t2=time.time()
            progress(f'SPF: {round(t2-t1,2)}, Time left: {round((len(files)-index)*(time.time()-t0)/(1+index)/60,2)} min. ',(index+1)/len(files))
            
            if opt.show_box and opt.crop:                                       #store debug images with bounding boxes
                index=0
                
                for b in vision.small:                                          #write first pass boxes
                    if opt.filter is None:
                        vision.frame=cv2.rectangle(vision.frame,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(255,0,0),4)
                    elif torch.argmax(vision.filtered[index])==1:               #passes filter
                        vision.frame=cv2.rectangle(vision.frame,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(255,0,0),4)  
                    index+=1

                for b in vision.medium:                                         #write second pass boxes
                    if opt.filter is None:
                        vision.frame=cv2.rectangle(vision.frame,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,255,255),4)
                    elif torch.argmax(vision.filtered[index])==1:               #passes filter
                        vision.frame=cv2.rectangle(vision.frame,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,255,255),4)
                    index+=1

                cv2.imwrite(f'{opt.dst}/boxes/{vision.file_name}.{index}.png',vision.frame)
        
        except Exception as e:
            print(file,e)
            try:
                file=file.replace('\\','/')
                name=file.split('/')[-1]
                    
                shutil.copy(file,f'{opt.dst}/misformated/{name}')
            except:Exception

if __name__ == "__main__":
    opt = parse_opt()
    main(opt) 
