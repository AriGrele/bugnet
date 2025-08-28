import shutil
import os
import re
import json
import cv2
import random
import math

def progress(text,percent,char='=',length=50): #display progress bar based on input percent 
    print(f'{text} |{math.floor(percent*length)*char}{math.ceil((1-percent)*length)*" "}| {round(percent*100,2)}%',end='     \r')

    if percent>=1:
        print()
    
def match(file, pattern): #returns true if any in [pattern] is found in file
    for search in pattern:
        if search in file.lower():return(True)
    return(False)

def load_json(path): #returns dict loaded from json file
    with open(path,'r') as labels:
        data=json.load(labels)

    return(data)

def clamp(x,l,u): #clamps value x between lower and upper bounds
    if x<l:return(l)
    if x>u:return(u)
    return x

def box(pos1,pos2): #(x1, y1) (x2, y2) to (x, y) (w, h)
    mid = [(pos2[0]+pos1[0])/2,(pos2[1]+pos1[1])/2]
    dim = [pos2[0]-pos1[0],pos2[1]-pos1[1]]
    return mid,dim
            
def unbox(center,dims,size=(1,1)): #(x, y) (w, h) to (x1, y1) (x2, y2)
    p1 = (clamp((center[0]-dims[0]/2)*size[1],0,1),clamp((center[1]-dims[1]/2)*size[0],0,1))
    p2 = (clamp((center[0]+dims[0]/2)*size[1],0,1),clamp((center[1]+dims[1]/2)*size[0],0,1))
    return p1,p2

def norm(b): #normalizes boxes so no points are outside range [0,1]
    p1,p2=unbox(b[0:2],b[2:4])
    m,d=box(p1,p2)
    return([m[0],m[1],d[0],d[1]])

def shuffle(dic): #randomizes dictionary order and returns .items()
    items=[(k,i) for k,i in dic.items()]
    random.shuffle(items)
    return(items)

def totxt(file): #converts expected image file names into .txt file names
    for end in ['.png','.jpg','.jpeg','.JPG','.PNG','.JPEG']:
        file=file.replace(end,'.txt')
    return(file)

def expand_name(classes):
    output=[classes[0]]

    for name in classes[1:]:
        output.append(f'{output[-1]}_{name}')

    return(output)
        
class dataset():
    def __init__(self,opt):
        self.opt   = opt
       
    def grab_images(self):
        
        images = [[f'{path[0]}/{x}'] for path in os.walk(self.opt.img_src) for x in path[2] if match(x, ['.png','.jpg','.jpeg'])]
        images = [x.replace('\\','/') for group in images for x in group]
        
        self.images = {x:x.split('/')[-1] for x in images}

    def grab_labels(self):
        labels      = [[f'{path[0]}/{x}' for x in path[2]] for path in os.walk(self.opt.ann_src) if any([match(file, ['json','txt']) for file in path[2]])]
        self.labels = [x.replace(self.opt.img_src,'').replace('\\','/') for group in labels for x in group]

        self.data={}
        for path in self.labels:
            label=load_json(path)
                
            if self.opt.skip_blank:
                
                items=[(k,i) for k,i in label.items()]
                
                for file,ann in items:
                    if len(list(ann))==0: #if there's no annotation for an image, delete
                        del label[file]

            if self.opt.skip_multi:
                
                items=[(k,i) for k,i in label.items()]
                
                for file,ann in items:
                    boxes=[a for a in ann if not 'Comment' in a]

                    if len(boxes)>1: #if there's more than one box in an image, delete
                        del label[file]

            self.data.update(label)
                
    def grab_comments(self):
        if not 'data' in vars(self):
            self.grab_labels()

        self.comments={}
        self.box_comments={}
        for file,data in self.data.items():
            comments=[re.findall('Comment_.+$',k)[0] for k in data.keys() if len(re.findall('Comment_.+$',k))>0]
            comments=[data[c] for c in comments]

            if len(comments)>0:
                self.comments[file]=comments[-1] ##popping [-1] in here for now as default behavior when multiple comments

            if not file in self.box_comments.keys():
                    self.box_comments[file]={}
                    
            for box,subdata in data.items(): #this may break under enet####
                   
                box_comments=[re.findall('Comment_.+$',k)[0] for k in subdata.keys() if len(re.findall('Comment_.+$',k))>0]
                box_comments=[subdata[c] for c in box_comments]

                if len(box_comments)>0:
                    self.box_comments[file][box]=box_comments[-1] ##popping [-1] in here for now as default behavior when multiple comments

    def grab_boxes(self):
        if not 'data' in vars(self):
            self.grab_labels()

        self.boxes={}
        for file,data in self.data.items():
            if len(data.keys())>0:
                if self.opt.box_comments:
                    self.boxes[file]={box_id:norm([float(x) for x in box['box']]) for box_id,box in data.items() if isinstance(box,dict)}

                else:
                    self.boxes[file]=[norm([float(x) for x in box['box']]) for _,box in data.items() if isinstance(box,dict)]
            else:
                self.boxes[file]=[]

    def make_classes(self):
        def map_renames(name,rename):
            for old,new in rename.items():
                name=re.sub(f'^{old}$',f'{new}',name)
                name=re.sub(f'_{old}$',f'_{new}',name)
                name=re.sub(f'^{old}_',f'{new}_',name)
                name=re.sub(f'_{old}_',f'_{new}_',name)

            return(name)
                
        self.classes={}

        if self.opt.rename!='':
            with open(self.opt.rename,'r') as text:
                rename={row[0]:row[1] for line in text if len(row:=line.strip().split(' '))>1}
                        
        if self.opt.dir_name:
            for path,file in self.images.items():
                subdirectory=path.replace(self.opt.img_src,'').split('/')[-2]

                if not file in self.classes.keys():
                    self.classes[file]=[]
                self.classes[file]+=subdirectory.split('_')

        if self.opt.img_name:
            for path,file in self.images.items():

                if not file in self.classes.keys():
                    self.classes[file]=[]
                self.classes[file]+=file.split('_')[:-1] #class name from all but the last item in filename separated by _

        if self.opt.comments:
            for path,file in self.images.items():
                
                if file in self.comments.keys():
                    if not file in self.classes.keys():
                        self.classes[file]=[]
                    self.classes[file]+=self.comments[file].split('_')

        if self.opt.box_comments:
            for path,file in self.images.items():
                
                if file in self.box_comments.keys():
                    for box,comment in self.box_comments[file].items():
                    
                        if not f'{file}_._{box}' in self.classes.keys():
                            self.classes[f'{file}_._{box}']=[]

                        self.classes[f'{file}_._{box}']+=comment.split('_')

        for file in self.classes.keys():
            self.classes[file]=expand_name(self.classes[file])

            if self.opt.rename!='':
                
                self.classes[file]=[map_renames(name,rename) for name in self.classes[file]]

        self.make_levels()

    def make_levels(self,negative=None): #negative indicates text search that will make the int mapping of the class -1; uses negative in name, so subtexts will match too
        levels={}
        for file,data in self.classes.items():
            for i,item in enumerate(data):

                if not i in levels.keys():
                    levels[i]=[]
                levels[i].append(item)

        self.classmap={k:[] for k in levels.keys()}
        for level,classes in levels.items():
            if not negative is None:
                unique=[x for x in list(set(classes)) if not negative in x] #skip unknowns
                self.classmap[level]={name:unique.index(name) for name in unique}

                for name in [x for x in list(set(classes)) if negative in x]: #only unknowns
                    self.classmap[level][name]=-1
            else:
                unique=list(set(classes))         
                self.classmap[level]={name:unique.index(name) for name in unique}

    def filter(self):

        ##count the number of images in each class for each level
        def count_classes(self): ##should prolly replace this with a higher level function at some point
            counts = {l:{} for l in self.classmap.keys()}

            for path,file in [(path,file) for path,file in self.images.items() if file in self.classes.keys()]:

                for level,name in enumerate(self.classes[file]):
                    if not name in counts[level].keys():
                        counts[level][name]=0
                        
                    counts[level][name]+=1

            return(counts)
        
        self.filters = {l:[] for l in self.classmap.keys()}
        self.unknown = {l:[] for l in self.classmap.keys()}
        
        counts=count_classes(self)
        
        ##lots of boilerplate here that should be cleaned up
        ##min_raw filtering
        for level,classes in counts.items():
            for name in classes.keys(): #check if number of images in class below min_raw threshold and accumulate by level
                
                if counts[level][name]<self.opt.min_raw:
                    self.filters[level].append(name)

            matched_files=[(path,file) for path,file in self.images.items() if file in self.classes.keys()]
            for path,file in matched_files: #check each image if class in this level in filters
                if self.classes[file][int(level)] in self.filters[level]:
                    del self.classes[file]

        ##unknown thresholding
        counts=count_classes(self)
        for level,classes in counts.items():
            for name in classes.keys():
                if counts[level][name]<self.opt.min_thresh:
                    self.unknown[level].append(name)

            matched_files=[(path,file) for path,file in self.images.items() if file in self.classes.keys()]
            for path,file in matched_files: #check each image if class in this level in filters
                if self.classes[file][int(level)] in self.unknown[level]:
                    last=self.classes[file][int(level)].split('_')[-1]
                    updated=re.sub(f'{last}$','unknown',self.classes[file][int(level)])
                    
                    self.classes[file][int(level)]=updated

        ##post threshold min and max
        levels=list(count_classes(self))
        for level in levels[::-1]: #start at lowest level in hierarchy and remove classes moving upwards
            counts=count_classes(self)[level]
            
            filters=[name for name,count in counts.items() if count<self.opt.min_final]

            matched_files=[(path,file) for path,file in self.images.items() if file in self.classes.keys()]
            caps={}
            for path,file in matched_files: #check each image if class in this level in filters
                taxon=self.classes[file][int(level)]
                if taxon in filters:
                    del self.classes[file]

                #if not taxon in caps.keys():
                #    caps[taxon]=0
                #caps[taxon]+=1

                #if caps[taxon]>self.opt.max_final:
                #    del self.classes[file]                

        self.make_levels('unknown') #replace unknown classes with -1
        
    def split(self):        
        train,val,test=[],[],[]
        self.splits={}

        files=[i for _,i in shuffle(self.images)]
        
        if self.opt.test_size>0:
            test_counts={}
            
            for file in [file for file in files if file in self.classes.keys()]:
                test_class=self.classes[file][-1]

                if not test_class in test_counts.keys():
                    test_counts[test_class]=0

                test_counts[test_class]+=1

                if test_counts[test_class]<=self.opt.test_size:
                    test.append(file)

            for file in test: #better ways to do this but quick to write
                files.remove(file)
        
        ntrain=clamp(int(len(files)*self.opt.split[0]),0,len(files))
        nval=int(len(files)*self.opt.split[1])
        
        if ntrain+nval>len(files):
            nval=clamp(int(len(files)-ntrain),0,len(files))

        
        while len(train)<ntrain:
            train.append(files.pop(0))
        while len(val)<nval:
            val.append(files.pop(0))

        train+=files #add remaining names to training set to account for rounding errors

        for i in train: self.splits[i]='train'
        for i in val:   self.splits[i]='val'
        for i in test:  self.splits[i]='test'

    def show_boxes(self):
        print('Saving example images')
        
        os.makedirs(f'{self.opt.dst}/example_boxes',exist_ok=True)

        files=[(path,file) for path,file in shuffle(self.images) if file in self.boxes.keys()]
        examples=files[:min(len(files),50)]
        
        for path,file in examples:
            img=cv2.imread(path,flags=cv2.IMREAD_UNCHANGED)
            y,x,c=img.shape

            if self.opt.box_comments:
                for _,box in self.boxes[file].items(): #data as x,y,w,h
                    b=[int(box[0]*x),int(box[1]*y),int(box[2]*x/2),int(box[3]*y/2)] #convert to px x,y,w/2,h/2
                    cv2.rectangle(img,(b[0]-b[2],b[1]-b[3]),(b[0]+b[2],b[1]+b[3]),(0,0,255),3)
            else:
                for box in self.boxes[file]: #data as x,y,w,h
                    b=[int(box[0]*x),int(box[1]*y),int(box[2]*x/2),int(box[3]*y/2)] #convert to px x,y,w/2,h/2
                    cv2.rectangle(img,(b[0]-b[2],b[1]-b[3]),(b[0]+b[2],b[1]+b[3]),(0,0,255),3)
                
            cv2.imwrite(f'{self.opt.dst}/example_boxes/boxed_{file}',img)

    def save(self):
        print('Saving annotations')
        for folder in ['train','val','test']:
            if self.opt.yolo:
                os.makedirs(f'{self.opt.dst}/localizer/images/{folder}',exist_ok=True)
            if self.opt.enet:
                os.makedirs(f'{self.opt.dst}/classifier/images/{folder}',exist_ok=True)

        if not self.opt.ann_src is None:  
            with open(f'{self.opt.dst}/merged_annotations.json','w') as file: #save merged json data
                json.dump(self.data,file,ensure_ascii=False,indent=4)

        yamlpath=os.path.abspath(self.opt.dst).replace('\\','/')

        ####
        if self.opt.yolo:
            for level,classes in self.classmap.items(): #yolo yaml format      
                with open(f'{self.opt.dst}/yolo_{level}.yaml','w') as out:
                    out.write('\n'.join([
                        f'train: {yamlpath}/localizer/images/train',
                        f'val: {yamlpath}/localizer/images/val',
                        f'nc: {len(classes)}',
                        f'names: {list(classes)}']))

            for i,(path,file) in enumerate(self.images.items()):
                
                progress('Yolo label progress:',(i+1)/len(list(self.images)))

                classfiles=[x.split('_._')[0] for x in self.classes.keys()]
                
                if file in classfiles and file in self.boxes.keys() and file in self.splits.keys(): ##need to go thru and remove duplicate code for non-box_comments settings
                    if self.opt.box_comments:
                        boxes={box_id:' '.join([str(x) for x in box]) for box_id,box in self.boxes[file].items()}
                    
                        for box_id,box in boxes.items():
                            index=[self.classmap[i][c] for i,c in enumerate(self.classes[f'{file}_._{box_id}'])]

                            for i,c in enumerate(index):
                                os.makedirs(f'{self.opt.dst}/localizer/labels_{i}/{self.splits[file]}',exist_ok=True) #save yolo labels
                                
                                with open(f'{self.opt.dst}/localizer/labels_{i}/{self.splits[file]}/{totxt(file).replace(" ","-")}','a') as out:
                                    text=f'{c} {box}\n'
                                    out.write(text)

                    else:
                        boxes=[' '.join([str(x) for x in box]) for box in self.boxes[file]]
                        index=[self.classmap[i][c] for i,c in enumerate(self.classes[file])]

                        for i,c in enumerate(index):
                            os.makedirs(f'{self.opt.dst}/localizer/labels_{i}/{self.splits[file]}',exist_ok=True) #save yolo labels
                            
                            with open(f'{self.opt.dst}/localizer/labels_{i}/{self.splits[file]}/{totxt(file).replace(" ","-")}','w') as out:
                                text='\n'.join([str(c)+' '+box for box in boxes])
                                out.write(text)

        ##format for EfficientNet
        if self.opt.enet:
            print(len([file for path,file in self.images.items() if file in self.classes.keys() and file in self.splits.keys()])) #n images
            
            with open(f'{self.opt.dst}/efficientnet.yaml','w') as out: #effnet yaml format
                
                out.write('\n'.join([
                    f'train: {yamlpath}/classifier/images/train',
                    f'val: {yamlpath}/classifier/images/val',
                    f'n: {[len([s for s in list(i) if not "unknown" in s]) for _,i in self.classmap.items()]}',
                    f'names: {[[s for s in list(i) if not "unknown" in s] for _,i in self.classmap.items()]}']))

            total=len(list(self.images))
            classkeys=self.classes.keys()
            splitkeys=self.splits.keys()

            os.makedirs(f'{self.opt.dst}/classifier/labels/test',exist_ok=True) #save enet labels
            os.makedirs(f'{self.opt.dst}/classifier/labels/train',exist_ok=True) #save enet labels
            os.makedirs(f'{self.opt.dst}/classifier/labels/val',exist_ok=True) #save enet labels
            
            for i,(path,file) in enumerate(self.images.items()):
                
                progress('Enet label progress:',(i+1)/total)

                if self.opt.crop:
                    if file in self.classes.keys() and file in self.boxes.keys(): #cropped labels
                    
                        index=[self.classmap[i][c] for i,c in enumerate(self.classes[file])] #currently no individual labels per box
                        os.makedirs(f'{self.opt.dst}/classifier/labels/{self.splits[file]}',exist_ok=True) #save enet labels
                        
                        for j,box in enumerate(self.boxes[file]): #data as x,y,w,h

                            filename=file.replace(" ","-").split('.')
                            ending=f'{j}.{filename.pop(-1)}'
                            name=totxt(f'{".".join(filename)}.{ending}')
                                    
                            with open(f'{self.opt.dst}/classifier/labels/{self.splits[file]}/{name}','w') as out:
                                text='\n'.join([str(i) for i in index])
                                out.write(text)
                    
                else: #uncropped labels
                    if file in classkeys and file in splitkeys:
                        index=[self.classmap[i][c] for i,c in enumerate(self.classes[file])]

                        with open(f'{self.opt.dst}/classifier/labels/{self.splits[file]}/{totxt(file).replace(" ","-")}','w') as out:
                            text='\n'.join([str(i) for i in index])
                            out.write(text)

        print('\nSaving images')
        os.makedirs(f'{self.opt.dst}/classifier/images/test',exist_ok=True) #save enet labels
        os.makedirs(f'{self.opt.dst}/classifier/images/train',exist_ok=True) #save enet labels
        os.makedirs(f'{self.opt.dst}/classifier/images/val',exist_ok=True) #save enet labels

        total=len(list(self.images))

        splitkeys=self.splits.keys()
        classfiles=[x.split('_._')[0] for x in self.classes.keys()]
        
        for i,(path,file) in enumerate(self.images.items()):

            progress('Image progress:',(i+1)/total)

            if file in classfiles and file in splitkeys:
                if self.opt.yolo and file in self.boxes.keys():
                    os.makedirs(f'{self.opt.dst}/localizer/images/{self.splits[file]}',exist_ok=True)
                    shutil.copy(path,f'{self.opt.dst}/localizer/images/{self.splits[file]}/{file.replace(" ","-")}')
                                               
                if self.opt.enet:
                    if self.opt.crop: #cropped images
                        if file in self.boxes.keys():
                            crop=cv2.imread(path)
                            y,x,_=crop.shape
                            
                            for j,box in enumerate(self.boxes[file]): #data as x,y,w,h
                                b=[int(box[0]*x),int(box[1]*y),int(box[2]*x/2),int(box[3]*y/2)] #convert to px x,y,w/2,h/2

                                try:
                                    cropped=crop[clamp(b[1]-b[3],0,y):clamp(b[1]+b[3],0,y),clamp(b[0]-b[2],0,x):clamp(b[0]+b[2],0,x)]

                                    filename=file.replace(" ","-").split('.')
                                    ending=f'{j}.{filename.pop(-1)}'
                                    name=f'{".".join(filename)}.{ending}'
                                   
                                    cv2.imwrite(f'{self.opt.dst}/classifier/images/{self.splits[file]}/{name}',cropped)
                                    
                                except Exception as e:
                                    pass                              

                            
                    else: #uncropped images
                        shutil.copy(path,f'{self.opt.dst}/classifier/images/{self.splits[file]}/{file.replace(" ","-")}')

