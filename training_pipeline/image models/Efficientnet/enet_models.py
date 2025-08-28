import torch
from torch import nn
from efficientnet_pytorch import EfficientNet

'''
NB this is mostly the same code as in utilities.enet_models.
Differences have creeped in organically due to different needs in training vs deployment, so -
This script should function for training models as described in the publication
utilities.enet_models should function for all deployment methods in database_pipeline and processing folders
If a model trained using this script fails to deploy properly in those folders, check that there is no new code here missing from utilities.enet_models, and vice versa.
'''

class Identity(nn.Module):                                                      #neural network layer where output == input. 
    
    def __init__(self):
        super(Identity,self).__init__()
        
    def forward(self,x):
        return(x)                                                               #for input x, return x


    
class E_model(nn.Module):                                                       #flat models - no hierarchy
    
    def __init__(self,n,groups,name='b0'):                                      #default smallest model if unspecified 
        super(E_model,self).__init__()
    
        if '_' in name:
            both=name.split('_')
            name=both[0]
            size=both[1]

        else:
            size='NA'
            
        self.n      = n                                                         #number of classes
        self.groups = groups                                                    #class names
        self.model  = EfficientNet.from_pretrained(f'efficientnet-{name}')      #load in model
        
        inf            = self.model._fc.in_features                             #pull out in features to define new layer of correct size
        self.model._fc = nn.Linear(inf,n,bias=True)                             #new final layer with n classes
           
        self.sm     = nn.Softmax(dim=1)

    def forward(self,x):
        x=self.model(x)
        return(self.sm(x))



class W_model(nn.Module):                                                       #wide models
    
    def __init__(self,n,groups,name='b0'):
        super(W_model,self).__init__()
        
        self.n      = n                                                         #definitions as in E_model
        self.groups = groups
        self.model  = EfficientNet.from_pretrained(f'efficientnet-{name}')
        
        inf            = self.model._fc.in_features
        self.model._fc = nn.Linear(inf,sum(n),bias=True)

        self.sm     = nn.Softmax(dim=1)

    def forward(self,x):
        if hasattr(self.model,'latent'):                                        #for post-training extraction of final layers for latent space clustering e.g. this has not been added to all classes, so look here if errors start cropping up in deployment. deployment code expects model to output tupple of (latent data, predictions)
            p = self.model(x)                                                   #penultimate layer
            x = self.model.final(p)                                             #ultimate layer

        else:
            p = False
            x = self.model(x)

        x=[self.sm(s) for s in torch.split(x,self.n,1)]                         #concat all taxon levels into wide format
        return((p,torch.cat(x,1)))

    def predict(self,x):
        x=self.model(x)

        x=[self.sm(s) for s in torch.split(x,self.n,1)]
        return(torch.cat(x,1))



class T_model(nn.Module):                                                       #funnel models
    
    def __init__(self,n,groups,name='b0'):
        super(T_model,self).__init__()
        self.n=n                                                                #definitions as in E_model
        self.groups=groups
        self.model=EfficientNet.from_pretrained(f'efficientnet-{name}')
        
        features=[self.model._fc.in_features]+n[::-1]                           #creates a structure where predictions at one taxonomic level affect prediciton of next
        self.lines=nn.ModuleList([nn.Linear(f,features[i+1],bias=True) for i,f in enumerate(features) if i<(len(features)-1)])
        self.model._fc=Identity()
        self.sm=nn.Softmax(dim=1)

    def forward(self,x):
        x=self.model(x)

        output=[]
        for line in self.lines:                                                 #each line here is a taxonomic level
            x=line(x)
            output.append(self.sm(x))
        return(torch.cat(output[::-1],1))

    def predict(self,x):
        x=self.model(x)

        output=[]
        for line in self.lines:
            x=line(x)
            output.append(self.sm(x))
        return(torch.cat(output[::-1],1))



class P_model(nn.Module):                                                       #pyramid models
    
    def __init__(self,n,groups,name='b0'):
        super(P_model,self).__init__()
        self.n=n                                                                #definitions as in E_model
        self.groups=groups
        self.model=EfficientNet.from_pretrained(f'efficientnet-{name}')
        
        features=[0]+n                                                          #creates a structure where predictions at one taxonomic level affect prediciton of next
        self.lines=nn.ModuleList([nn.Linear(f+self.model._fc.in_features,features[i+1],bias=True) for i,f in enumerate(features) if i<(len(features)-1)])
        self.model._fc=Identity()
        
        self.sm=nn.Softmax(dim=1)

    def forward(self,x):
        x=self.model(x)

        penultimate=x.clone().detach()
        x=self.lines[0](x)
        
        output=[x]
        for line in self.lines[1:]:                                             #each line here is a taxonomic level
            x=line(torch.cat([penultimate,x],1))
            output.append(x)

        for i,o in enumerate(output):
            output[i]=self.sm(o)
            
        return(torch.cat(output,1))

    def predict(self,x):
        x=self.model(x)

        penultimate=x.clone().detach()
        x=self.lines[0](x)
        
        output=[x]
        for line in self.lines[1:]:
            x=line(torch.cat([penultimate,x],1))
            output.append(x)

        for i,o in enumerate(output):
            output[i]=self.sm(o)
            
        return(torch.cat(output,1))



class F_model(nn.Module):                                                       #full hierarchy models - here be dragons
    
    def __init__(self,n,groups,tree,device,name='b0'):
        
        def clamp(x,l,u):                                                       #clamp a value x between l and u
            if x<l:return(l)
            elif x>u:return(u)
            return(x)

        ##there are a few python libraries for dealing with hierarchical dicts, but none of them quite handle the data as it needs to be for integration with the rest of the training code
        ##so - quick and dirty code below for building taxonomic trees and passing data through them

        def nest(v):                                                            #builds a nested dict representing a taxonomic hierarchy
            v=[x for x in v]                                                    #clone list of keys
            val=v.pop(0)
            if len(v)>0:
                return({val:nest(v)})                                           #recursivly build out nested dict from tree names
            return({val:{}})                                                    #leaves of tree are empty dicts
                
        def merge(a,b,tree=None):                                               #for merging two nested tree dicts
            if tree is None:tree=[]
            for key in b:
                if key in a:
                    if isinstance(a[key],dict) and isinstance(b[key],dict):     #avoid attempting to merge items of tree which are not subdicts
                        merge(a[key],b[key],tree+[str(key)])                    #recursivly apply to each sub level of the hierarchy 
                else:
                    a[key]=b[key]
            return(a)

        def search(tree,device,layer={},path='',n=1280):                        #build a series of nested nn layers based on input hierarchy 
            key=tree.keys()

            for k in key:
                layer[path+str(k)]=nn.Linear(n+1,clamp(len(tree[k].keys()),1,10**10),bias=True).to(device)
                layer=search(tree[k],device,layer,str(path)+str(k),n)           #recursivly build next layer based on current
            return(layer)
        
        super(F_model,self).__init__()
        self.n=n                                                                #definitions as in E_model
        self.groups=groups
        self.device=device
        self.model=EfficientNet.from_pretrained(f'efficientnet-{name}')

        self.tree={}                                                            #init empty hierarchy
        for i in tree:                                                          #for taxon names (pulled from yaml), construct hierachy tree
            self.tree=merge(self.tree,nest(i))

        self.lines=search(self.tree,self.device,n=self.model._fc.in_features)   #convert tree to nn layers
        self.final=nn.Linear(self.model._fc.in_features,n[0],bias=True)         #as with E_model
        self.model._fc=Identity()

        self.sm=nn.Softmax(dim=1)

    def forward(self,x):
        x=self.model(x)
        self.penultimate=x.clone().detach()                                     #for working with latent data

        x=self.final(x)
        
        xdict,upper=self.forward_tree(self.tree,x)                              #special forward function for the crazy nn structure this class of model uses
    
        keys=[x for _,x in sorted(zip([len(k) for k in xdict],xdict))]          #sort keys by len

        output=[xdict[k][:,xdict[k].size()[1]-1] for k in keys]                 #convert forward tree output to match wide format
        return(torch.stack(output,1))
    
    def forward_tree(self,tree,result,xdict={},upper={'':torch.tensor([1])},path=''): #to naviage tree structure, forward must 1) run the current layer 2) figure out which outputs from current layer feed into which inputs for next layer(s)
        key=sorted(list(tree))                                                  #get everything in standard order
        upper[path]=upper[path].to(self.device)                                 #pull a top level layer in tree structure
    
        if len(key)>0:
            
            if result.size()[1]>1:                                              #branches
                upper.update({path+str(key[i]):torch.mul(x,upper[path]) for i,x in enumerate(torch.split(result,1,1))}) #we hold two dicts here, one for current layer and one for previous
                xdict.update({path+str(key[i]):torch.cat([self.penultimate,upper[path+str(key[i])]],1) for i,x in enumerate(torch.split(result,1,1))})
                
            else:                                                               #leaves
                upper[path+str(key[0])]=torch.mul(result,upper[path])
                xdict[path+str(key[0])]=torch.cat([self.penultimate,upper[path+str(key[0])]],1)

            for k in key:
                line=self.sm(self.lines[path+str(k)](xdict[path+str(k)]))       #softmax to entire line as defined above
                xdict,upper=self.forward_tree(tree[k],line,xdict,upper,str(path)+str(k))

        return(xdict,upper)

    def predict(self,x):                                                        #as above
        x=self.model(x)
        self.penultimate=x.clone().detach()

        x=self.final(x)
        
        xdict,upper=self.forward_tree(self.tree,x)
    
        keys=[x for _,x in sorted(zip([len(k) for k in xdict],xdict))]

        output=[self.sm(xdict[k][:,xdict[k].size()[1]-1]) for k in keys]
        return(torch.stack(output,1))
        