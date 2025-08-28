import argparse
import os
from   utilities.format_data import dataset

def parse_opt():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--img_src',    type=str,   default='images',   help='Path to folder of images or folder of folders of images')
    parser.add_argument('--ann_src',    type=str,   default=None,       help='Path to folder of JSON or txt annotation files')
    parser.add_argument('--dst',        type=str,   default='datasets', help='Path to output folder')
    parser.add_argument('--test_size',  type=int,   default=0,          help='Number of images to split from each lowest class as a test set')
    parser.add_argument('--split',      type=tuple, default=(.9,.1),    help='Percent values for tain, val, and test sets. test_size overwrites')
    parser.add_argument('--min_thresh', type=int,   default=400,        help='Minimum number of values in a class to replace with unknown, non-inclusive')
    parser.add_argument('--min_raw',    type=int,   default=0,          help='Minimum number of values in a class to delete, non-inclusive')
    parser.add_argument('--min_final',  type=int,   default=0,          help='Minimum number of values in a class to delete post merging unknowns, non-inclusive')
    parser.add_argument('--max_final',  type=int,   default=2000,       help='maximum number of values in a class to delete post merging unknowns, non-inclusive')
    parser.add_argument('--rename',     type=str,   default='',         help='directory of txts containing rename mappings')

    parser.add_argument('--show_boxes',   action='store_true',          help='Save example images with box annotations')
    parser.add_argument('--dir_name',     action='store_true',          help='Use the name of the image folder as part of the taxon name')
    parser.add_argument('--img_name',     action='store_true',          help='Use the name of the image file as part of the taxon name')
    parser.add_argument('--comments',     action='store_true',          help='Use the annotated comments as part of the taxon name')
    parser.add_argument('--box_comments', action='store_true',          help='Use the annotated comments as part of the taxon name')
    parser.add_argument('--yolo',         action='store_true',          help='format for yolo')
    parser.add_argument('--enet',         action='store_true',          help='format for efficientnet')
    parser.add_argument('--skip_blank',   action='store_true',          help='skip unannotated images')
    parser.add_argument('--skip_multi',   action='store_true',          help='skip multiple boxes for enet')
    parser.add_argument('--crop',         action='store_true',          help='crop boxes for enet')
    
    return(parser.parse_args())
    
def main(opt):
    os.makedirs(opt.dst,exist_ok=True)
    
    formatter=dataset(opt)
    
    print('Grabbing image files')
    formatter.grab_images()                                                     #stores {path:imagefile} dict as self.images

    if not opt.ann_src is None:
        print('Grabbing annotations')
        formatter.grab_comments()                                               #stores {imagefile:comment} dict as self.comments
        formatter.grab_boxes()                                                  #stores {imagefile:[boxes]} dict as self.boxes
              
    formatter.make_classes()                                                    #stores {imagefile:class} dict as self.classes
    formatter.filter()                                                          #filter images by min threshold, min raw, renames
    
    print('Splitting out train / val / test sets')
    formatter.split()                                                           #create mapping from image name to train / val / test set
    
    if opt.show_boxes:
        formatter.show_boxes()

    formatter.save()

if __name__ == "__main__":
    opt=parse_opt()
    main(opt)   
