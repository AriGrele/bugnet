#Web scraping

##process_images.py

Main python script for cropping and classifiying insects from images. NB this script currently requires a model yaml file in this directory which contains a list of class numbers in each taxonomic level and a dict of taxon names. This can be copied directly from the training data. 

##Example useage:

```
process_images.py --images "../data/input" --yolo_weights "../data/models/yolo5_m.pt" --enet_weights "../data/models/finals.model.pt" --dst "../data/output" --resolution 3200 --filter "../data/models/binary_filter.4/best_model.pt" --static --crop
```

Which will take all images in all folders in the input dir, localize insects at a resolution of 3200, crop them out and classify them, and cluster detect insects across frames

##Arguments

```
images       - image folder. Can contain subfolders with images.
yolo_weights - path to localizer model file
enet_weights - path to classifier model file
dst          - destination folder for data
resolution   - resolution for yolo model
conf         - YOLO confidence threshold
iou          - YOLO iou threshold
filter       - binary filter model path
enet_res     - resolution for EfficientNet model
show_box     - shows bounding boxes in debug images
crop         - classify, or crop and classify?
just_big     - only the largest pass for localizing insects
just_small   - only the smallest pass for localizing insects
static       - cluster insects across frames
resize       - resize the input image to the model resolution    
```

