# Web scraping

## scrape_gbif.py

Main python script for scraping data from GBIF. Allows downloading of data only, images, summarizing taxon richness for GBIF downloads, and combinations thereof. 

## Example useage:

```
scrape_gbif.py --getdata --getimages --trim --dst "../data/database_pipeline" --yolo_weights ../data/models/yolo5_m.pt --full_weights "../data/models/uncropped_gbif_image_classifier.pt" --enet_weights "../data/models/cropped_gbif_image_classifier.pt" --coord (-3.1190,-60.0217) --spprange 0.001 --genrange 0.005 --cap 1000 
```

Which will download data for all insect species within 0.001 degrees of Manaus, Brazil, all insect genera within 0.005 degrees of Manaus, and download up to 1,000 images per taxon. Note the range here is very small to make running the example faster - when filtering to just the order Lepidoptera, this should still find ~1.7 million observations, of which ~25,000 have usable images. A more reasonable range for large models would be 5 degrees for species and 15 degrees for genera, which should return millions of usable images. 

NB, these downloads can take a *long* time. Expect each github search to take 15 min - 3 hours to complete, depending on size. Download speeds will depend on internet speed and hardware, but image downloads may take as much as 1 second per image on some machines.

## Arguments

```
coord       	  - central location coordinates (lat / long)
spprange     	  - degree range to search for species
genrange     	  - degree range to search for genera
cap          	  - maximum number of image results per species
getdata      	  - download gbif data from search
getimages    	  - download gbif images from search
summarize    	  - summarize taxon richness from search
trim              - crop insects from images
yolo_weights      - path to localizer model file
enet_weights      - path to cropped image filter model
uncropped_weights - path to uncropped image filter model
dst               - destination folder for data
resolution        - image resolution for YOLO model
conf              - YOLO confidence threshold
iou               - YOLO iou threshold
```

