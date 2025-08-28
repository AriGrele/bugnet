import shutil,argparse

'''
This script is just to help move image folders around when training lots of models.
Essentially, this allows training from a single directory by sequentially moveing image folders into that dir,
training a model on that dir, and then clearing out those images for the next batch
'''

def main(opt):
    try:
        shutil.rmtree(opt.dst)
    except:Exception
    shutil.copytree(opt.src,opt.dst)

def parse_opt():
    parser=argparse.ArgumentParser()
    parser.add_argument('src',type=str,default='',help='source folder')
    parser.add_argument('dst',type=str,default='',help='destination folder')
    return parser

if __name__=="__main__":
    opt=parse_opt().parse_args()
    main(opt)



