import torch
from torch import nn
from efficientnet_pytorch import EfficientNet

class Identity(nn.Module):
    
    def __init__(self):
        super(Identity,self).__init__()
        
    def forward(self,x):
        return(x)
    
class E_model(nn.Module):
    
    def __init__(self,n,name='b0'):
        super(E_model,self).__init__()
        self.model=EfficientNet.from_pretrained(f'efficientnet-{name}')
        
        inf=self.model._fc.in_features
        self.model._fc = nn.Linear(inf,n,bias=True)

        self.sm=nn.Softmax(dim=1)


    def forward(self,x):
        x=self.model(x)
        return(self.sm(x))

class W_model(nn.Module):
    
    def __init__(self,n,name='b0'):
        super(W_model,self).__init__()
        self.n=n
        self.model=EfficientNet.from_pretrained(f'efficientnet-{name}')
        
        inf=self.model._fc.in_features
        self.model._fc = nn.Linear(inf,sum(n),bias=True)

        self.sm=nn.Softmax(dim=1)

        
        input(self.model)

    def forward(self,x):
        input('model: ',self.model)
        
        x=self.model(x)

        x=[self.sm(s) for s in torch.split(x,self.n,1)]
        return(torch.cat(x,1))

class T_model(nn.Module):
    
    def __init__(self,n,name='b0'):
        super(T_model,self).__init__()
        self.model=EfficientNet.from_pretrained(f'efficientnet-{name}')
        
        features=[self.model._fc.in_features]+n[::-1]
        self.lines=nn.ModuleList([nn.Linear(f,features[i+1],bias=True) for i,f in enumerate(features) if i<(len(features)-1)])
        self.model._fc=Identity()
        self.sm=nn.Softmax(dim=1)

    def forward(self,x):
        x=self.model(x)

        output=[]
        for line in self.lines:
            x=line(x)#self.sm(line(x))
            output.append(x)
        return(torch.cat(output[::-1],1))

class P_model(nn.Module):
    
    def __init__(self,n,name='b0'):
        super(P_model,self).__init__()
        self.model=EfficientNet.from_pretrained(f'efficientnet-{name}')
        
        features=[0]+n
        self.lines=nn.ModuleList([nn.Linear(f+self.model._fc.in_features,features[i+1],bias=True) for i,f in enumerate(features) if i<(len(features)-1)])
        self.model._fc=Identity()
        self.sm=nn.Softmax(dim=1)

    def forward(self,x):
        x=self.model(x)

        penultimate=x.clone().detach()
        x=self.sm(self.lines[0](x))
        
        output=[x]
        for line in self.lines[1:]:
            x=line(torch.cat([penultimate,x],1))#self.sm(line(torch.cat([penultimate,x],1)))
            output.append(x)
        return(torch.cat(output,1))

class F_model(nn.Module):
    
    def __init__(self,n,tree,device,name='b0'):
        
        def clamp(x,l,u):
            if x<l:return(l)
            elif x>u:return(u)
            return(x)

        def nest(v):
            v=[x for x in v]
            val=v.pop(0)
            if len(v)>0:
                return({val:nest(v)})
            return({val:{}})
                
        def merge(a,b,tree=None):
            if tree is None:tree=[]
            for key in b:
                if key in a:
                    if isinstance(a[key],dict) and isinstance(b[key],dict):
                        merge(a[key],b[key],tree+[str(key)])
                else:
                    a[key]=b[key]
            return(a)

        def search(tree,device,layer={},path='',n=1280):
            key=tree.keys()

            for k in key:
                layer[path+str(k)]=nn.Linear(n+1,clamp(len(tree[k].keys()),1,10**10),bias=True).to(device)
                layer=search(tree[k],device,layer,str(path)+str(k),n)
            return(layer)
        
        super(F_model,self).__init__()
        self.device=device
        self.model=EfficientNet.from_pretrained(f'efficientnet-{name}')

        self.tree={}
        for i in tree:
            self.tree=merge(self.tree,nest(i))

        self.lines=search(self.tree,self.device,n=self.model._fc.in_features)
        self.final=nn.Linear(self.model._fc.in_features,n[0],bias=True)
        self.model._fc=Identity()

        self.sm=nn.Softmax(dim=1)

    def forward(self,x):
        x=self.model(x)
        self.penultimate=x.clone().detach()

        x=self.final(x)#self.sm(self.final(x))
        
        xdict,upper=self.forward_tree(self.tree,x)
    
        keys=[x for _,x in sorted(zip([len(k) for k in xdict],xdict))]

        for k,i in upper.items():print(k,i)

        print(upper)
        output=[xdict[k][:,xdict[k].size()[1]-1] for k in keys]
        print(output)
        return(torch.stack(output,1))
    
    def forward_tree(self,tree,result,xdict={},upper={'':torch.tensor([1])},path=''):
        key=sorted(list(tree))
        upper[path]=upper[path].to(self.device)

        if len(key)>0:
            if result.size()[1]>1:
                upper.update({path+str(key[i]):torch.mul(x,upper[path]) for i,x in enumerate(torch.split(result,1,1))})
                xdict.update({path+str(key[i]):torch.cat([self.penultimate,upper[path+str(key[i])]],1) for i,x in enumerate(torch.split(result,1,1))})
                
            else:
                upper[path+str(key[0])]=torch.mul(result,upper[path])
                xdict[path+str(key[0])]=torch.cat([self.penultimate,upper[path+str(key[0])]],1)

            for k in key:
                line=self.sm(self.lines[path+str(k)](xdict[path+str(k)]))
                xdict,upper=self.forward_tree(tree[k],line,xdict,upper,str(path)+str(k))

        return(xdict,upper)
        
