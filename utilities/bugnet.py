import cv2
import torch
import time
import os
import re
import sys

from torch import nn
from PIL   import Image
from efficientnet_pytorch   import EfficientNet
from torchvision.transforms import ToTensor

sys.path.insert(0, './utilities')

from   utilities.models    import yolo
from   utilities.functions import area, bb_iou
import utilities.enet_models

class Identity(nn.Module):                                                      #nn layer that returns input as output
    
    def __init__(self):
        super(Identity,self).__init__()
        
    def forward(self,x):
        return(x)

def fix_rotation(im):                                                           #standardize image rotation
        y,x,_=im.shape

        if y>x:
            im=cv2.rotate(im,rotateCode=cv2.ROTATE_90_CLOCKWISE)

        return(im)
    
class Bugnet:
    def __init__(self,opt):
        self.device="cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using {self.device} device")
 
        self.images       = opt.images
        self.yolo_weights = opt.yolo_weights
        self.enet_weights = opt.enet_weights
        self.dst          = opt.dst
        self.split_n      = opt.split_n
        self.resolution   = opt.resolution
        self.resize       = opt.resize
        self.classifier   = opt.classifier
        self.filter       = opt.filter
        self.crop         = opt.crop
        self.enet_res     = opt.enet_res
        self.sizes        = opt.sizes
        
        self.frame,self.frames,self.boxes_s,self.boxes_m = [],[],[],[]          #for holding image and bounding box data
        
        self.errors = 'errors.txt'
        self.stamp  = 'none'
        self.levels = ['Class','Order','Family','Genus','Species']              #taxonomic level labels

        self.yolo = torch.load(self.yolo_weights,weights_only=False)            #object localizer
        
        self.yolo.conf = opt.conf                                               #overwrite default yolo parameters
        self.yolo.iou  = opt.iou

        if self.classifier=='enet':                                             #holdover from plan to allow other classification models, e.g. classifications from yolo itself
            self.enet = torch.load(self.enet_weights,weights_only=False)

            if type(self.enet.model._fc)==torch.nn.modules.container.Sequential: #covers some edge cases for backwards compatability 
                self.enet.model.final=self.enet.model._fc[1]
                self.enet.model._fc[1]=Identity()
                
            else:
                self.enet.model.final=self.enet.model._fc
                self.enet.model._fc=nn.Sequential(Identity(),Identity())
                
            self.enet.model.latent=True

        if not self.filter is None:                                             #model for filtering low-quality crops
            self.filternet = torch.load(self.filter,weights_only=False)

        self.l_eval()
        
        if not os.path.exists(self.errors):                                     #error logging
            with open(self.errors,'w') as e:e.write('errors\n')

        if not os.path.exists(self.dst):                                        #output folder
            os.makedirs(self.dst,exist_ok=True)

        with open(f'{self.dst}/data.txt','w') as out:                           #class probabilities file
            out.write('')

    def l_eval(self):                                                           #set to evaluation mode
        self.yolo.eval()
        if self.classifier=='enet':                                             #as above
            self.enet.eval()
        if not self.filter is None:
            self.filternet.eval()
                          
    def grab_insects(self,file):                                                #for list of frames, localize insects, classify insects, store images and predictions
        try:
            if type(file) is str:
                self.file_name='.'.join(file.split('/')[-1].split('.')[:-1])    #ugly
                self.frame=fix_rotation(cv2.imread(file))                       #standardize rotation
            
            dim=self.frame.shape[0:2]                                           #extract image dimensions for rescaling
            factor=self.resolution/min(dim)                                     #to maintain aspect ratio

            t=208                                                               #hardcoded value for filtering outputs of the large and small localization passes - may need to change but this value is good for 16MP images
            if self.resize:                                                     #resize based on smallest dim, keeping aspect ratio
                self.frame = cv2.resize(self.frame,(int(dim[1]*factor),  int(dim[0]*factor)))
                t*=factor     
                
            with torch.no_grad():
                if self.crop:                                                   #set to crop out objects
                    self.boxes_s=self.yolo(self.frame,size=(int(dim[0]*factor),  int(dim[1]*factor)))   #smallest pass
                    self.boxes_m=self.yolo(self.frame,size=(int(dim[0]*factor/8),int(dim[1]*factor/8))) #largest pass

                    if self.sizes[0]: t=0                                       #just big thresh
                    if self.sizes[1]: t=9999**2                                 #just small thresh

                    self.small  = [((b[0]),(b[1]),(b[2]),(b[3]),b[4]) for ind,box in enumerate(self.boxes_s.xyxy) for b in box if area(b)<t*t]
                    self.medium = [((b[0]),(b[1]),(b[2]),(b[3]),b[4]) for ind,box in enumerate(self.boxes_m.xyxy) for b in box if area(b)>t*t] #using medium and big interchangably here, sorry
            
                    for s in self.small:                                        #delete mediums that are likely the same as smalls
                        for i,m in enumerate(self.medium):
                            if bb_iou(s,m)>0.6:
                                del self.medium[i]

                    if self.sizes[0]:                                           #just big pass NB big pass gives small objects and vice versa due to how localization works with resolution - may cause some confusion in how pass vs output names work
                        self.small  = []
                    if self.sizes[1]:
                        self.medium = []

                    self.boxes   =  self.small+self.medium                      #combine both passes
                    self.insects = [(self.frame[int(b[1]):int(b[3]),int(b[0]):int(b[2])],b[4]) for b in self.boxes] #crop original image to list of insects

                else:                                                           #empty output if no cropping
                    self.boxes_s = []
                    self.boxes_m = []
                    self.boxes   = []
                    self.insects = [(self.frame,1)]                             #store entire frame for classification

                if len(self.insects)>0 and self.classifier=='enet':             #if there are any insects -

                    self.insectsquare = torch.stack([(ToTensor()(cv2.resize(img,(self.enet_res,self.enet_res)))).to(self.device) for img,conf in self.insects]) #rescale
                    self.filtersquare = torch.stack([(ToTensor()(cv2.resize(img,(self.enet_res,self.enet_res)))).to(self.device) for img,conf in self.insects]) #rescale
                    
                    self.insectsquare = torch.split(self.insectsquare,64)       #batch by 64 - hardcoded so may need to change if memory issues
                    self.filtersquare = torch.split(self.filtersquare,64)

                    outputs = [self.enet(group) for group in self.insectsquare] #classifications for each insect
   
                    self.morphospace = torch.cat([x[0] for x in outputs])       #latent space data
                    self.prediction  = torch.cat([x[1] for x in outputs])       #class predictions

                    if not self.filter is None:
                        self.filtered = torch.cat([self.filternet(group)[1] for group in self.filtersquare]) #only second item
                    else:
                        self.filtered = torch.tensor([[0,1]*self.prediction.shape[0]]) #if no filter, pass all items
                else:
                    self.prediction = None
                            
        except Exception as e:
            print('error:',e)
            self.prediction=None
            with open(self.errors,'a') as log:
                log.write(f'{time.time()} {file} {e}\n')
