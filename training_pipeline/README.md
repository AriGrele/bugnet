# Model training

## format_json_for_models.py

Main python script for formatting image annotations for training YOLO or EfficientNet models. Allows annotations in the form of json files, nested folders, or image names in the style of "taxon_lower-taxon_lowest-taxon_ID.jpg", for any number of taxonomic levels. 

## Example useage:

```
format_json_for_models.py --img_src "../data/database_pipeline/good" --dst "../data/training_data" --min_thresh 100 --min_final 0 --max_final 2000 --test_size 10 --enet --dir_name
```

Which will format annotations for training an Efficientnet, taking taxonomic information from the names of the images in the input folder. Additionally, if there are fewer than 100 images representing a taxon, all images of that taxon will be labeled as "unknown". No classes will be dropped due to low image counts, and no more than 2000 images will be included per taxon. 10 images per taxon will be split out into a testing set (seperate from the training and validation sets)

## Arguments

```
img_src      - Path to folder of images or folder of folders of images
ann_src      - Path to folder of JSON or txt annotation files
dst          - Path to output folder
test_size    - Number of images to split from each lowest class as a test set
split        - Percent values for tain, val, and test sets. test_size overwrites
min_thresh   - Minimum number of values in a class to replace with unknown, non-inclusive
min_raw      - Minimum number of values in a class to delete, non-inclusive
min_final    - Minimum number of values in a class to delete post merging unknowns, non-inclusive
max_final    - maximum number of values in a class to delete post merging unknowns, non-inclusive
rename       - directory of txts containing rename mappings
show_boxes   - Save example images with box annotations
dir_name     - Use the name of the image folder as part of the taxon name
img_name     - Use the name of the image file as part of the taxon name
comments     - Use the annotated comments as part of the taxon name
box_comments - Use the annotated box comments as part of the taxon name
yolo         - format for yolo
enet         - format for efficientnet
skip_blank   - skip unannotated images
skip_multi   - skip images with multiple boxes for enet
crop         - crop boxes for enet
```

