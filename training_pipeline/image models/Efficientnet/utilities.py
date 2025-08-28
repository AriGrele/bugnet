import math
import torch
import time
import argparse
import os
import re
import shutil

from torch import nn
from torcheval import metrics

def progress(text,percent,char='=',length=20,end='\r'):                         #progress bar
    if percent==1 and end=='\r':
        end = '\n'
    return(f'{text} |{math.floor(percent*length)*char}{math.ceil((1-percent)*length)*" "}| {round(percent*100,2)}%  '+end)

def fix_unknowns_ground(index,n,g,unknown):                                     #adjust labels based on "unknown" approach

    output  = []
    species = [x for x in n]                                                    #copy
    groups  = [x for x in g]

    match unknown:
        case 'classes':                                                         #one unknown class in each level
            
            species[1:] = [s+1 for s in species[1:]]                            #one unknown col per level

            fullgroups = [x[:] for x in groups]
            fullgroups = [fullgroups[0]]+[x+[f'{["family","genus","species"][j]}_unknown'] for j,x in enumerate(fullgroups[1:])] #really silly
            groups     = [x[:] for x in fullgroups]
            
            for i,value in enumerate(index):
                section=torch.tensor([0]*species[i])
                section[value]=1

                output.append(section)
                
        case 'subclasses':                                                      #unique unknown class in each category

            species[1:] = [s+species[i] for i,s in enumerate(species[1:])]      #one unknown col per level for each class in higher level
            
            fullgroups=[x[:] for x in groups]
            for level in range(1,len(groups)):
                unknowns = [f'{x}_unknown' for x in groups[level-1]][::-1]
                fullgroups[level] += unknowns
                
            groups=[x[:] for x in fullgroups]                                   #silly

            for i,value in enumerate(index):
                
                if value<0:
                    value=value*(index[i-1]+1)
                    
                section=torch.tensor([0]*species[i])
                section[value]=1

                output.append(section)
        
        case 'zero':                                                            #all zero within level
            for i,value in enumerate(index):
                section=torch.tensor([1e-6]*species[i])                         #very small non-zero value

                if value>-1:                                                    #unknowns stay zeros
                    section[value]=1

                output.append(section)
        
        case 'random':                                                          #all random [0,1] within level
            for i,value in enumerate(index):
                section=torch.tensor([0]*species[i])
                section[value]=1

                if value<0:                                                     #leaving a marker to be resolved each time loss is calculated
                    section=torch.tensor([-1]*species[i])

                output.append(section)
        
        case 'subrandom':                                                       #all random [0,1] within category           
            for i,value in enumerate(index):
                section=torch.tensor([0]*species[i])
                
                if value<0:                                                     #leaving a marker to be resolved each time loss is calculated                    
                    upper=groups[i-1][index[i-1]]
                    lower=[i for i,x in enumerate(groups[i]) if upper in x]

                    for taxon in lower:
                        section[taxon]=-1

                else:
                    section[value]=1

                output.append(section)
        
        case 'uniform':                                                         #all 1/n within level
            for i,value in enumerate(index):
                section=torch.tensor([0]*species[i])
                section[value]=1

                if value<0:                                                     #1/n where n is the total number of classes in level
                    section=torch.tensor([1/species[i]]*species[i])

                output.append(section)
        
        case 'subuniform':                                                      #all 1/n within category
            for i,value in enumerate(index):
                section=torch.tensor([0]*species[i])
                
                if value<0:                                                     #1/n where n is the number of taxa in catagory within level                 
                    upper=groups[i-1][index[i-1]]
                    lower=[i for i,x in enumerate(groups[i]) if upper in x]

                    for taxon in lower:
                        section[taxon]=1/len(lower)

                else:
                    section[value]=1

                output.append(section)

        case 'ignore':                                                          #unknowns do not contribute to loss
            for i,value in enumerate(index): 
                section=torch.tensor([0]*species[i])
                
                if value<0:
                    section[value]=-1                                           #leaving a marker to be resolved each time loss is calculated        
                else:
                    section[value]=1
                    
                output.append(section)
                
    return(species,groups,output)

def fix_unknowns_loss(y,pred,species,loss_fn,unknown):                          #calculate loss based on "unknown" approach

    match unknown:
        case 'classes':                                                         #unique unknown class in each category
            loss=[loss_fn(group.float(),y[i].float()) for i,group in enumerate(pred)]
                
        case 'subclasses':                                                      #unique unknown class in each level
            loss=[loss_fn(group.float(),y[i].float()) for i,group in enumerate(pred)]
        
        case 'zero':                                                            #all zero within level
            loss=[loss_fn(group.float(),y[i].float()) for i,group in enumerate(pred)]
        
        case 'random':                                                          #all random [0,1] within level
            ground=[]
            for i,group in enumerate(pred):
                randoms=torch.rand(y[i].shape).to(y[i].get_device())            #random tensor of same size as ground tensor
                ground.append(torch.abs(torch.mul(y[i],randoms)))

            loss=[loss_fn(group.float(),ground[i].float()) for i,group in enumerate(pred)] 
                
        case 'subrandom':                                                       #all random [0,1] within category   
            ground=[]
            for i,group in enumerate(pred):
                randoms=torch.rand(y[i].shape).to(y[i].get_device())            #random tensor of same size as ground tensor
                ground.append(torch.abs(torch.mul(y[i],randoms)))

            loss=[loss_fn(group.float(),ground[i].float()) for i,group in enumerate(pred)] 
        
        case 'uniform':                                                         #all 1/n within level
            loss=[loss_fn(group.float(),y[i].float()) for i,group in enumerate(pred)]
        
        case 'subuniform':                                                      #all 1/n within category
            loss=[loss_fn(group.float(),y[i].float()) for i,group in enumerate(pred)]

        case 'ignore':                                                          #unknowns do not contribute to loss
            loss=[]
            for i,group in enumerate(pred):
                losses=loss_fn(group[torch.all(y[i]>-1,dim=1)].float(),y[i][torch.all(y[i]>-1,dim=1)].float())
                loss.append(losses)

    return(loss)
