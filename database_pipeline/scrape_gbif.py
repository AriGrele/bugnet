import os
import re
import argparse
import csv
import requests
import time
import cv2
import random
import torch
import sys
import numpy as np

from collections import Counter
from torchvision.transforms import ToTensor

sys.path.append("..")                                                           #to load classes from higher dir. Silly, but makes certain aspects of the code easier down the line than other package based methods

import utilities.enet_models
from   utilities.GBIF      import GBIF
from   utilities.functions import progress
from   utilities.bugnet    import Bugnet

def parse_opt():                                                                #cmd line input arguments
    parser = argparse.ArgumentParser()

    ##scraping arguments
    parser.add_argument('--coord',       type=str,    default='(0,0)',  help='central location coordinates (lat / long)')
    parser.add_argument('--spprange',    type=float,  default='1',      help='degree range to search for species')
    parser.add_argument('--genrange',    type=float,  default='5',      help='degree range to search for genera')
    parser.add_argument('--cap',         type=float,  default='2000',   help='maximum number of results per species')

    parser.add_argument('--getdata',      action='store_true',          help='download gbif data from search') 
    parser.add_argument('--getimages',    action='store_true',          help='download gbif images from search') 
    parser.add_argument('--summarize',    action='store_true',          help='summarize taxon richness from search') 
    parser.add_argument('--trim',         action='store_true',          help='crop insects from images') 

    ##model arguments #not all of these are used here, but makes syncing with other scripts easier
    parser.add_argument('--images',       type=str,   default='images', help='image folder')
    parser.add_argument('--yolo_weights', type=str,   default='',       help='path to localizer model file')
    parser.add_argument('--enet_weights', type=str,   default='',       help='path to insect filter model file')
    parser.add_argument('--full_weights', type=str,   default='',       help='path to image filter model file')
    parser.add_argument('--dst',          type=str,   default='output', help='destination folder for data')
    parser.add_argument('--split_n',      type=tuple, default=(1,1),    help='x,y splits for input frame')
    parser.add_argument('--resolution',   type=int,   default=416,      help='resolution for yolo model')
    parser.add_argument('--classifier',   type=str,   default='enet',   help='set to "yolo" to use species level yolo classifier')
    parser.add_argument('--conf',         type=float, default=0.25,     help='YOLO confidence threshold')
    parser.add_argument('--iou',          type=float, default=0.45,     help='YOLO iou threshold')
    parser.add_argument('--filter',       type=str,   default=None,     help='binary filter path')
    parser.add_argument('--enet_res',     type=int,   default=256,      help='resolution for yolo model')
    
    parser.add_argument('--show_box',     action='store_true',          help='shows bounding boxes in debug images')    
    parser.add_argument('--subfolders',   action='store_true',          help='image folder')    
    parser.add_argument('--crop',         action='store_true',          help='classify, or crop and classify?')    
    parser.add_argument('--just_big',     action='store_true',          help='only the largest pass for localizing insects')    
    parser.add_argument('--just_small',   action='store_true',          help='only the smallest pass for localizing insects')    
    parser.add_argument('--static',       action='store_true',          help='cluster insects across frames')  
    parser.add_argument('--resize',       action='store_true',          help='resize the input image to the model resolution')   
    return(parser.parse_args())

def scrape_data(opt):
    ##authentification
    with open('input/gbif_auth.txt','r') as gbif_auth:                          #username, password, and email for GBIF
        auth=[line.strip() for line in gbif_auth]
        
        os.environ['GBIF_USER']  = auth[0]
        os.environ['GBIF_PWD']   = auth[1]
        os.environ['GBIF_EMAIL'] = auth[2]



    ##load filters
    with open('input/order_filter.txt') as data:                                #search for insects in these orders
        order_filter=[line.strip().lower() for line in data]

    with open('input/family_filter.txt') as data:                               #remove insects in these families
        family_filter=[line.strip().lower() for line in data]

    with open('input/license_filter.txt') as data:                              #remove images outside of these licenses
        license_filter=[line.strip().lower() for line in data]



    ##species search
    local_taxa = GBIF(eval(opt.coord))                                          #start a new GBIF search at these coords
    local_taxa.region(['taxonKey = 216'],float(opt.spprange))                   #filter to insects within range of center coords
    local_taxa.get(columns=['taxonKey','order','family','genus','species'])     #extract data

    species=local_taxa.unique('species')

    print(f'{local_taxa.data.shape[0]} local species observations')



    ##genus search
    if len(local_taxa.unique('species'))>0:                                     #added this in here because when genus grabing was in the same env level as species grabing, GBIF returned an empty csv file
        local_taxa.region(['taxonKey = 216'],float(opt.genrange))
        local_taxa.concat(columns=['taxonKey','order','family','genus','species'])

        print(f'{local_taxa.data.shape[0]} local species and genus observations')
    
        local_taxa.filter('order',order_filter)                                 #ONLY include orders in this list
        local_taxa.filter('family',family_filter,'out')                         #do NOT include families in this list

    local_taxa.write('../data/database_pipeline/local_taxa.csv')                #list of all taxa found from search - but not all observations of these taxa



    ##global search
    print('Searching for local taxa in global database')

    all_taxa=GBIF()                                                             #start a new GBIF search, globally

    local=local_taxa.unique('taxonKey')
    query={'type':'and',                                                        #globally, find all obs of the returned taxa with images
           'predicates': [
               {'type': 'or', 'predicates': [{'type':'equals','key':'TAXON_KEY','value':name} for name in local if str(name)!='nan']},
               {'type':'equals','key':'MEDIA_TYPE','value':'StillImage'}]}
    
    all_taxa.download(query,output='DWCA')                                      #download in Darwin Core format
    all_taxa.get('multimedia.txt',['gbifID','type','identifier','license'])     #grab observation images
    all_taxa.merge('occurrence.txt',['gbifID','order','family','genus','species'],'gbifID') #merge with observation taxonomic data

    all_taxa.write('../data/database_pipeline/complete_all_taxa.csv')           #save a csv of all observations of taxa of interest, with image URIs and taxonomic information

    try:                                                                        #wrapping these in try-catches due to encoding errors in gbif data
        with open('../data/database_pipeline/licenses.txt','w', encoding='utf-8') as out:
            out.write('\n'.join([str(x) for x in all_taxa.unique('license')]))
            
    except Exception as e: print(e)

    try:
        with open('../data/database_pipeline/family.txt','w', encoding='utf-8') as out:
            out.write('\n'.join([str(x) for x in all_taxa.unique('family')]))
            
    except Exception as e: print(e)

    all_taxa.filter('license',license_filter)                                   #remove images which cannot be used due to license
    all_taxa.filter('type',['stillimage'])                                      #remove other media types
    all_taxa.filter('identifier',['',' '],'out')                                #remove unknown identifiers

    all_taxa.data.loc[~(all_taxa.data['species'].isin(species)),'species']='unknown' #ensure that if a species is not abundant enough, but the genus is, we keep the genus known and drop the species name

    for taxon in ['order','family','genus','species']:                          #standardize treatment of unknown taxon names => "unknown"
        all_taxa.data.loc[all_taxa.data[taxon].isnull(),taxon]='unknown'
        all_taxa.filter(taxon,[str(name).lower() for name in local_taxa.unique(taxon)+['unknown','unknownspp']])

    for taxon in ['order','family']:                                            #remove unknown orders and families
        all_taxa.filter(taxon,['unknown'],'out')



    ##apply caps
    all_taxa.data=all_taxa.data.sample(frac=1).reset_index(drop=True)           #randomize order
    all_taxa.data['count']=all_taxa.data.groupby(['order','family','genus','species']).cumcount()+1 #add column of 1:N for N observations
    all_taxa.filter('count',int(opt.cap),'<=')                                  #only include the first X observations out of those N
    
    all_taxa.write('../data/database_pipeline/all_taxa.csv')                    #csv of filtered taxa

def scrape_images(opt):

    device="cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using {device} device")

    
    with open('../data/database_pipeline/image_errors.txt','w') as errors:
        errors.write('')

    with open('../data/database_pipeline/all_taxa.csv',newline='') as csvfile:
        reader=csv.reader(csvfile,delimiter=',',quotechar='|')
        all_taxa=[row for row in reader if len(row)>0 and row[0]!='gbifID']



    print('Randomizing list of taxa')
    random.shuffle(all_taxa)                                                    #randomizing doesn't change anything at this point, but makes download homogenous so the data can still be used if interupted

    vision = Bugnet(opt)                                                        #class for cropping and classifying images
    uncropped_class = torch.load(opt.full_weights, weights_only = False)        #model for filtering entire images
    uncropped_class.eval()
    
    downloaded = os.listdir(f'{opt.dst}/bad_full')+os.listdir(f'{opt.dst}/good')+os.listdir(f'{opt.dst}/bad') #avoid downloading already downloaded images
    downloaded = [x.split('_')[-1].split('.')[0] for x in downloaded]


    
    print(len(downloaded))
    print(len(all_taxa))
    
    for i,row in enumerate(all_taxa):
        url = row[2]
        gbifID = row[0]
        taxon  = f'{row[4]}_{row[5]}_{row[6]}_{row[7]}'.replace(' ','-')        #all taxonomic info

        name   = f'{taxon}_{gbifID}'                                            #unique taxon + id name

        if gbifID in downloaded:
            pass
            
        else:
            if 'http' in url:
                try:
                    progress(f'{url:<80}',(i+1)/len(all_taxa))
                    wait=time.time()                                            #track time to set rate limit
                        
                    img_data    = requests.get(url,timeout=10).content          #request image content, skip if delay between reads>n seconds
                    image_array = np.asarray(bytearray(img_data),dtype=np.uint8)
                    image       = cv2.imdecode(image_array,-1)                  #read directly to cv2 for first pass binary filter

                    formatted_img=(ToTensor()(cv2.resize(image,(512,512)))).to(device).unsqueeze(0)
                    uncropped_pred=torch.argmax(uncropped_class.predict(formatted_img)[1]).item() #current model output is names: [['Bad', 'Good']]

                    if uncropped_pred==1:                                       #if the full image looks useable -
                        with open(f'{opt.dst}/{name}.{i}.jpg','wb') as handler: #save to file where filename = id
                            handler.write(img_data)                             #writing a file and deleting it after trimming is easier than converting a byte string to a cv2 image 
                        
                        if opt.trim:                                            #if set to trim out insects
                            vision.grab_insects(f'{opt.dst}/{name}.{i}.jpg')

                            if len(vision.insects)==1:                          #only save insects when there's exactly one - avoids empty images and images where identity can't be confirmed unsupervised

                                cropped_pred=torch.argmax(vision.prediction)    #classes are swapped here: names: [['Good', 'Bad']] ##This will break something if you retrain the models!!

                                if cropped_pred==0:                             #if the cropped insect looks usable -
                                    cv2.imwrite(f'{opt.dst}/good/{name}.{i}.jpg',vision.insects[0][0])
                                else:
                                    cv2.imwrite(f'{opt.dst}/bad/{name}.{i}.jpg',vision.insects[0][0]) #save potentially bad crops to another folder

                            os.remove(f'{opt.dst}/{name}.{i}.jpg')              #delete the full image

                    else:
                        with open(f'{opt.dst}/bad_full/{name}.{i}.jpg','wb') as handler: #save bad images to check
                            handler.write(img_data) 
                            
                    wait=.5-(time.time()-wait)                                  #wait if process has taken < 0.5 seconds to set rate limits                                  #NB much of GBIF images are hosted via AWS where there is essentially no rate limit, so this may not be necessary e.g. for just inat images
                    if wait>0:
                        time.sleep(wait)
                            
                except Exception as e:
                    with open('../data/database_pipeline/image_errors.txt','a') as errors:
                        errors.write(f'{e} {url}\n')                            #log errors    

def summarize_data(opt):                                                        #helpful to know what you're actually getting from your search
    with open('../data/database_pipeline/all_taxa.csv',newline='') as csvfile:
        reader=csv.reader(csvfile,delimiter=',',quotechar='|')
        all_taxa=[row for row in reader if len(row)>0 and row[0]!='gbifID']

    n_image = len(all_taxa)                                                     #number of images
    order   = [x[4] for x in all_taxa if not 'unknown' in x]                    #number of orders, etc
    family  = ['_'.join(x[4:6]) for x in all_taxa if not 'unknown' in x]
    genus   = ['_'.join(x[4:7]) for x in all_taxa if not 'unknown' in x]
    species = ['_'.join(x[4:8]) for x in all_taxa if not 'unknown' in x]

    print('Number of images:', n_image,'\n')

    print('Number of orders:',   len(list(set(order))))
    print('Number of families:', len(list(set(family))))
    print('Number of genera:',   len(list(set(genus))))
    print('Number of species:',  len(list(set(species))))

    print()

    for k,i in Counter([x[4] for x in all_taxa]).items():                       # image counts by order
        print(f'{k:<30} {i}')

    input('Enter to continue')

if __name__ == "__main__":
    opt = parse_opt()

    opt.just_small = True                                                       #sets localizer model to single pass 
    opt.sizes=[opt.just_big,opt.just_small]                                     #for using only low/high res passes
    opt.crop = opt.trim                                                         #synonym for backwards compat. 
    
    if not os.path.exists(f'{opt.dst}/good'):                                   #output folders
        os.makedirs(f'{opt.dst}/gbif_downloads')                                #folder for Darwin Core zips from GBIF
        os.makedirs(f'{opt.dst}/good')                                          #training images
        os.makedirs(f'{opt.dst}/bad')                                           #bad crops
        os.makedirs(f'{opt.dst}/bad_full')                                      #bad full images pre-cropping. these bad images are mostly useful for training future filters
 
    if opt.getdata:
        scrape_data(opt)

    if opt.summarize:
        summarize_data(opt)

    if opt.getimages:
        scrape_images(opt)

print('Scraping complete')
