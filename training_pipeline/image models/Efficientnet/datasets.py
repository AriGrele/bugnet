import yaml
import cv2
import torch
import os
import math
import random

import utilities

from   torch.utils.data import Dataset
import torchvision.transforms as transforms

def progress(percent,char='=',length=50):                                       #progress bar. At some point, replace individual definitions of this function with calls to utilities.functions.progress
    print(f'|{math.floor(percent*length)*char}{math.ceil((1-percent)*length)*" "}| {round(percent*100,2)}%     ',end='\r')
    if percent==1:print()

def read_yaml(file):                                                            #Safeload of yaml file
    with open(file,"r") as d:
        try:return(yaml.safe_load(d))
        except Exception as e:print(e)

class data(Dataset):                                                            #main class for working with datasets via pytorch
    def __init__(self,file,item,res,augment,unknown):
        print(f'\nloading {item}\n')
        
        self.item    = item                                                     #eval for evaluation, train/val for training
        self.res     = (res,res)                                                #image resolution
        self.augment = augment                                                  #augmentation T/F
        self.unknown = unknown                                                  #loss funciton for unknowns

        if item=='eval':
            self.imgdir = file
            self.label  = {f:f for f in os.listdir(self.imgdir)}                #load image labels as dict from input dir
            self.label_keys = list(self.label)
            
        else:
            self.data   = read_yaml(file)                                       #formated yaml file
            self.n      = self.data['n']                                        #taxa counts
            self.groups = self.data['names']                                    #taxa names
            self.imgdir = self.data[item]                                       #image director as stored in yaml

            self.label  = self.read_lab()                                       #function to load in labels depends on str and model class
            self.label_keys = list(self.label)

        self.files = os.listdir(self.imgdir)                                    #image files

    def __len__(self): return(len(self.files))                                  #length function

    def __getitem__(self,i):                                                    #for grabing image / label pairs from training data folder
        path=self.files[i]

        check=0                                                                 #messy way of dealing with image corruption
        while check==0:
            try:
                image=cv2.resize(cv2.imread(f'{self.imgdir}/{path}'),self.res)  #load and resize image
                check=1

            except Exception:
                path=random.choice(self.files)                                  #if error when loading image, try random image. ~1/10,000 GBIF images are corrupt and not caught by previous filters, so this is a quick way to avoid errors without greatly biasing training data. should avoid this method if greater propurtions of images throw errors
                i=self.files.index(path)
                
        if self.augment:                                                        #apply standard augmentation suite
            aug=[transforms.ToPILImage(),transforms.RandAugment(magnitude=10)]
            transform=transforms.Compose(aug+[transforms.ToTensor()])           #apply random image augmentation and tensor transform to images

        else:
            transform=transforms.Compose([transforms.ToTensor()])
            
        image=transform(image)

        label=self.label[self.label_keys[i]]
        
        return(image,label)

class flat(data):                                                               #no hierarchy
    def read_lab(self):
        out={}
        file=self.imgdir.replace('images','labels')
        files=os.listdir(file)
        
        for lab in files:
            progress(files.index(lab)/len(files))
            with open(f'{file}/{lab}','r') as line:
                index=int([x.strip().split(' ')[0] for x in line][-1])          #last item of first row in .txt file
                out[lab]=torch.tensor([0]*max(self.n))
                out[lab][index]=1
                
        return(out)

class wide(data):                                                               #all taxon levels in parallel, via various methods as defined in enet_models
    def read_lab(self):
        out={}
        file=self.imgdir.replace('images','labels')

        self.indeces=[]
        files=os.listdir(file)
        total=len(files)
        
        for i,lab in enumerate(files):
            progress((i+1)/total)

            old_classes={}
            
            with open(f'{file}/{lab}','r') as line:
                if self.unknown=='old':                                         #old method - unused and will probably break if you try using it
                    index=[int(x.strip().split(' ')[0]) for x in line]

                    current=''
                    for i,value in enumerate(index):
                        if not i in old_classes.keys():
                            old_classes[i]={}

                        current+=(str(value)+'_')
                        if not curent in old_classes[i].keys():
                            old_classes[i][current]=0
                        old_classes[i][current]+=1

                else:
                    index=[int(x.strip().split(' ')[0]) for x in line]          #first item of every row in .txt file
                    self.indeces.append(index)

                    species,groups,l = utilities.fix_unknowns_ground(index,self.n,self.groups,self.unknown)

                    l=torch.cat(l)

            out[lab]=l

        self.species = species                                                  #update taxa counts by output of fix_unknowns
        self.groups  = groups
        
        return(out)
