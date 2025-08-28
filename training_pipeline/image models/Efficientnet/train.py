import datasets
import enet_models as models
from utilities import progress, fix_unknowns_loss

import time
import argparse
import os
import math
import re
import shutil

import torch
from torch import nn
from torch.utils.data import DataLoader
from torch.nn.functional import one_hot
from torcheval import metrics
from torch.nn.functional import normalize

def parse_opt():
    parser=argparse.ArgumentParser()

    parser.add_argument('--data',     type=str, default='data.yaml',       help='Path to yaml data file')
    parser.add_argument('--img_size', type=int, default=256,               help='image resolution')
    parser.add_argument('--model',    type=str, default='b0',              help='Efficientnet model architecture')
    parser.add_argument('--dst',      type=str, default='.',               help='folder to save model weights')
    parser.add_argument('--epochs',   type=int, default=100,               help='number of training epochs')
    parser.add_argument('--weights',  type=str, default='best_model.pt',   help='starting weights')
    parser.add_argument('--str',      type=str, default='flat',            help='hierarchy structure - flat, simple, wide, funnel, pyramid, or full')
    parser.add_argument('--unknown',  type=str, default='classes',         help='unknown algorithm')
    
    parser.add_argument('--augment',  action='store_true',                 help='apply image augmentation when training')

    return(parser.parse_args())

class Handler:
    def __init__(self,device,opt):
        self.device     = device
        self.data       = opt.data
        self.img_size   = opt.img_size
        self.str        = opt.str
        self.epochs     = opt.epochs
        self.loss_fn    = nn.MSELoss()                                          #find MSE works better here for the specific way loss handles unknowns in these models
        self.net        = opt.model
        self.weights    = opt.weights
        self.dst        = opt.dst
        self.augment    = opt.augment
        self.unknown    = opt.unknown
        self.batchsize  = 64                                                    #hardcoded batchsize for stochastic gradient descent
        
        self.loss_xy = {'train':[[],[]],'val':[[],[]]}
        self.acc_xy  = {'train':[[],[]],'val':[[],[]]}

        self.hierarchy()                                                        #define model class and dataset structure based on hierarchy str

        if not os.path.exists(opt.dst):                                         #output folder
            os.mkdir(opt.dst)
            
        with open(f'{self.dst}/results_{self.str}.txt','w') as results:
            results.write('epoch level train.loss train.accuracy val.loss val.accuracy\n')
            
    def load(self,Class):                                                       #load in training / val data based on specific model class requirements
        self.training_data = Class(self.data,'train',self.img_size,self.augment,self.unknown)
        self.training_data.species = self.training_data.species                 #classes
        
        self.val_data      = Class(self.data,'val',self.img_size,False,self.unknown)
        
        self.training      = DataLoader(self.training_data,batch_size=self.batchsize,shuffle=True)
        self.validation    = DataLoader(self.val_data,     batch_size=self.batchsize,shuffle=True)

    def hierarchy(self): 
        match self.str:
            case 'flat':
                self.load(datasets.flat)
                self.model      = models.E_model(max(self.training_data.species),self.training_data.groups,name=self.net).to(self.device)        
                self.optimizer  = torch.optim.SGD(self.model.parameters(),lr=1) #hardcoded learning rates, may need adjusting 
                self.scheduler  = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer,T_max=self.epochs,eta_min=1e-4)
                
            case 'wide':
                self.load(datasets.wide)
                self.model      = models.W_model(self.training_data.species,self.training_data.groups,name=opt.model).to(self.device)
                self.optimizer  = torch.optim.SGD(self.model.parameters(),lr=2)
                self.scheduler  = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer,T_max=self.epochs,eta_min=1e-2)

            case 'funnel':
                self.load(datasets.wide)
                self.model      = models.T_model(self.training_data.n,self.training_data.groups,name=self.net).to(self.device)
                self.optimizer  = torch.optim.SGD(self.model.parameters(),lr=.2)
                self.scheduler  = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer,T_max=self.epochs,eta_min=1e-2)

            case 'pyramid':
                self.load(datasets.wide)
                self.model      = models.P_model(self.training_data.n,self.training_data.groups,name=self.net).to(self.device)
                self.optimizer  = torch.optim.SGD(self.model.parameters(),lr=.2)
                self.scheduler  = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer,T_max=self.epochs,eta_min=1e-2)

            case 'full':
                self.load(datasets.wide)
                tree=self.training_data.indeces+self.val_data.indeces
                self.model      = models.F_model(self.training_data.n,self.training_data.groups,tree,self.device,name=opt.model).to(self.device)
                self.optimizer  = torch.optim.SGD(self.model.parameters(),lr=10)
                self.scheduler  = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer,T_max=self.epochs,eta_min=1e-2)

            case _:
                print('structure must be one of flat, simple, wide, funnel, pyramid, full. defaulting to flat')
                self.str='flat'                                                 #if invalid str parameter, use "flat"
                self.hierarchy()
        
    def train(self,epoch):
        self.size=0                                                             #acumulate these in loop so batch plots calculate averages correctly
        self.num_batches=0
        
        species = self.training.dataset.species                                 #classes
        test_loss,correct,pool=[0 for x in species],[0 for x in species],[[] for x in species] #most models take list of outputs, each item being a taxonomic level
        
        if self.str=='flat':                                                    #for flat, unlisted
            species=[species[-1]]
            test_loss,correct=[0],[0]

        self.model.train()

        t0 = time.time()                                                        #for fps calc
        for batch,(X,y) in enumerate(self.training):
   
            self.size+=X.shape[0]
            self.num_batches+=1

            X,y=X.to(self.device),y.to(self.device)

            pred = self.model(X)[1]
            
            pred=torch.split(pred,species,1)                                    #split output into sections for each taxonomic level based on class counts
            y=torch.split(y,species,1)

            losses = fix_unknowns_loss(y,pred,species,self.loss_fn,self.unknown) #specific loss calc based on "unknowns"

            loss=sum([l*[.1,.1,.4,.4][i] for i,l in enumerate(losses)])         #weight lower levels higher

            
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            for i,l in enumerate(losses):
                if torch.isnan(l).item(): losses[i]=0                           #zeros for loss where all samples removed
                else: losses[i]=l.item()
                
            for i,group in enumerate(pred):
                test_loss[i] += losses[i]                                       #separate loss for display. I don't know why I'm doing this
                groupmax      = torch.argmax(group[torch.any(y[i]>1e-6,dim=1)],dim=1) #remove rows which are all zero or any negatives before accuracy calc
                ymax          = y[i][torch.any(y[i]>1e-6,dim=1)]
                pool[i].append(sum([groupmax[j] in torch.nonzero(row==torch.max(row)) for j,row in enumerate(ymax)])/self.batchsize*100) #if there are multiple correct values in y, pred is true if it matches any

                if len(pool[i])>100:
                    del pool[i][0]
                    
                correct[i] = sum(pool[i])/len(pool[i])

            print(progress(f'Epoch: {epoch}, Loss {",".join([f"{x:.3f}" for x in test_loss])} | Acc {",".join([f"{x:.3f}" for x in correct])} | Progress:',(batch+1)/len(self.training)),end='\r')

        with open(f'{self.dst}/results_{self.str}.txt','a') as results:
            for i,loss in enumerate(test_loss):
                text=f'{epoch} {i} {loss} {correct[i]} NA NA\n'
                results.write(text)
                    
        
        self.scheduler.step()                                                   #decay learning rate
        
        
    def validate(self,epoch):                                                   #mostly the same as train
        
        self.model.eval()
        
        self.size=0                                                             #acumulate these in loop so batch plots calculate averages correctly
        self.num_batches=0
        
        species=self.training.dataset.species
        test_loss,correct=[0 for x in species],[0 for x in species]

        if self.str=='flat':
            species=[species[-1]]
            test_loss,correct=[0],[0]
        
        t0=time.time()
        with torch.no_grad():
            for batch,(X,y) in enumerate(self.validation):
   
                self.size+=X.shape[0]
                self.num_batches+=1

                X,y=X.to(self.device),y.to(self.device)

                pred = self.model(X)[1]
                pred = torch.split(pred,species,1)
                y    = torch.split(y,species,1)

                losses = fix_unknowns_loss(y,pred,species,self.loss_fn,self.unknown)

                for i,l in enumerate(losses):
                    if torch.isnan(l).item(): losses[i]=0                       #zeros for loss where all samples removed
                    else: losses[i]=l.item()
                    
                for i,group in enumerate(pred):
                    test_loss[i] += losses[i]                                   #separate loss for display #i don't know why I'm doing this
                    groupmax      = torch.argmax(group[torch.any(y[i]>1e-6,dim=1)],dim=1) #remove rows which are all zero or any negatives before accuracy calc
                    ymax          = y[i][torch.any(y[i]>1e-6,dim=1)]
                    correct[i]   +=sum([groupmax[j] in torch.nonzero(row==torch.max(row)) for j,row in enumerate(ymax)]) #if there are multiple correct values in y, pred is true if it matches any
                
                print(progress(f'Validation: Loss {",".join([f"{x:.3f}" for x in test_loss])} | Acc {",".join([f"{100*x/self.size:.3f}" for x in correct])} | Progress:',(batch+1)/len(self.validation)),end='\r')
            
        with open(f'{self.dst}/results_{self.str}.txt','a') as results:
            for i,loss in enumerate(test_loss):
                text=f'{epoch} {i} NA NA {loss} {100*correct[i]/self.size}\n'
                results.write(text)
                    

        print()
        return(test_loss)                                                       #return a value here so we can choose the best model

    def process(self):
        score=10**10
        os.system('cls' if os.name == 'nt' else 'clear')
        
        for t in range(self.epochs):
            
            self.train(t)
            new_score=self.validate(t)

            if sum(new_score)<=score:                                           #compare val loss in each epoch to find cummulative min
                score=sum(new_score)
                torch.save(self.model,f'{self.dst}/best_model.pt')
            
            torch.save(self.model,f'{self.dst}/last_model.pt')                  #save most recent model regardless of loss     

def main(opt):
    device="cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using {device} device")

    handler=Handler(device,opt)
    print(handler.model,end='\n\n\n')
    time.sleep(5)                                                               #just to read model info
    handler.process()                                                           #train and validate the models  

    print('\n'*20)

if __name__=='__main__':
    opt=parse_opt()
    main(opt)
