import os,shutil,math,json,random,csv,cv2
'''
NB that some functions here are not called in any script, but may be useful for moving data around
e.g. just call random_subset via a new script or cmdline to manually pull images to a new folder when necessary
'''

def progress(text,percent,char='=',length=50):                                  #display progress bar based on input percent 
    print(f'{text} |{math.floor(percent*length)*char}{math.ceil((1-percent)*length)*" "}| {round(percent*100,2)}%',end='     \r')
    if percent>=1:print()

def random_subset(src,n,dst):                                                   #select a random subset of images and copy to dst
    print('searching for files')
    files=[os.path.join(dp, f).replace('\\','/') for dp, dn, fn in os.walk(src) for f in fn]
    print(len(files))
    files=list(set(files))[:n]

    for i,file in enumerate(files):
        name=file.split('/')[-1]

        shutil.copy(file,f'{dst}/{name}')

def populate_ann(file,src,dst):                                                 #replace annotations with no label (e.g. :{}) with box that fills entire image
    with open(file,'r') as ann:
        ann=json.load(ann)

    files=os.listdir(src)
    output={}
    
    for i,(image,data) in enumerate(ann.items()):
        comments=list(data)

        output[f'{i}.jpg']={"1":{"box": [.5,.5,1,1],"user": "human"}}
        

        if image in files and len(comments)>0:
            group=data[comments[0]]

            if not os.path.exists(f'{dst}/{group}'):
                os.makedirs(f'{dst}/{group}',exist_ok=True)

            shutil.copy(f'{src}/{image}',f'{dst}/{group}/{i}.jpg')

    name=file.replace('\\','/').split('/')[-1]
    updated=file.replace(name,f'updated_{name}')
    
    with open(updated,'w') as o:
        json.dump(output,o,ensure_ascii=False,indent=4)

def remove_corrupt(src):                                                        #check if images can be read by opencv and delete if not
    files=os.listdir(src)

    for i,file in enumerate(files):
        print(i/len(files))
        im=cv2.imread(f'{src}/{file}')

        if im is None:
            print(i,file)
            os.remove(f'{src}/{file}')


def gridify(src,dst,size=832):                                                  #split images into grid of equal squares
    if not os.path.exists(dst):
        os.mkdir(dst)

    for image in os.listdir(src):
        try:
            img=cv2.imread(f'{src}/{image}')

            if random.randrange(0,1)<.5:                                        #flip 50% of images
                img=cv2.flip(img,0)
            
            dim=img.shape

            for x in range(dim[1]//size):
                for y in range(dim[0]//size):
                    print(dim,x*size,y*size,x*size+size,y*size+size)
                    
                    new=img[int(y*size):int(y*size+size),int(x*size):int(x*size+size)]
                    ny,nx,_=new.shape

                    if ny==nx:
                        cv2.imwrite(f'{dst}/{image.lower().replace(".jpg","")}_{x}_{y}.jpg',new)
        except:Exception
                
def randomize_img(src):                                                         #add random index number to each image name
    images=os.listdir(src)

    for img in images:
        os.rename(f'{src}/{img}',f'{src}/{random.randrange(0,100000)}_{img}')


def yolo_to_json(src,dst):                                                      #convert yolo data format to json
    
    for folder in os.listdir(src):
        files=os.listdir(f'{src}/{folder}/labels')
        print(folder,len(files))

        data={}
        for i,file in enumerate(files):
            if i%100==0:print(i/len(files))
            with open(f'{src}/{folder}/labels/{file}','r') as lines:
                data[file.replace('.txt','.jpg')]={(i+1):[float(x) for x in lines.strip().split()[1:5]] for i,lines in enumerate(lines)}

        i=int(folder.replace("exp",""))
        with open(f'{dst}/batch_{i-1}.json','w') as output:
            json.dump(data,output)

def resize(src,size):                                                           #resize all img in sr dir to new dims
    files=os.listdir(src)
    
    for i,image in enumerate(files):
        print(i/len(files))
        img=cv2.imread(f'{src}/{image}')

        img=cv2.resize(img,size)

        cv2.imwrite(f'{src}/{image}',img)

def reorder(box):                                                               #standardize order of corner points in bounding box
    return((min(box[0],box[2]),min(box[1],box[3]),max(box[0],box[2]),max(box[1],box[3])))

def bb_iou(a,b):                                                                #calculate intersection over union from two bounding boxes
    box_a=reorder(a)
    box_b=reorder(b)
    
    xA = max(box_a[0], box_b[0])
    yA = max(box_a[1], box_b[1])
    xB = min(box_a[2], box_b[2])
    yB = min(box_a[3], box_b[3])
	
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
	
    boxAArea = (box_a[2] - box_a[0] + 1) * (box_a[3] - box_a[1] + 1)
    boxBArea = (box_b[2] - box_b[0] + 1) * (box_b[3] - box_b[1] + 1)
	
    return(interArea / float(boxAArea + boxBArea - interArea))


def area(b):                                                                    #area of bounding box
    w=b[2]-b[0]
    h=b[3]-b[1]
    return((w*h).item())