# BugNet data pipeline

These folders contain scripts and a small number of trained models for creating training datasets, training, and deploying BugNet models.
There are additionally example batch files in each folder demonstrating the creation from scratch of a small classification model. See

* database_pipeline/scrape_images.bat
* training_pipeline/format.bat
* training_pipeline/image models/Efficientnet/Train.bat
* processing_pipeline/run.bat

Running these files with the current parameters will produce a dataset of ~13,000 images of Lepidoptera, format these data for training a classification model, train a classification model with ~28 species, and use this model to classify insects in an example camera trap image.

## Folders
### Annotation_pipeline

Contains software for annotating images with bounding box data for training new localization models and taxonomic data for training and validating classification models. 

### Database_pipeline

Contains scripts for scraping data and images from GBIF. The pipeline can be set to download GBIF datasets only, images only, or both in sequence. Data can be filtered to include specific insect orders, image licenses, or exclude specific insect families. Images can be stored as the entire image file, or individual insects can be cropped from the downloaded images. Regardless, all images are passed through a quality filter to remove e.g. blurry images, images of larvae, and other low-quality data.

### Training_pipeline

Contains scripts for training YOLO localization models and EfficientNet classification models. The pipeline includes a script for formatting data to the specific requirements of each model type taking data from multiple annotation formats. 

### Processing_pipeline

Contains a script for taking in camera trap images, cropping, and classifying insects from those images. The script can be set to apply multiple size passes to localize insects over a large range of sizes, can be set to filter out low quality crops, and can cluster insects across multiple frames if the image stream represents a static camera position with multiple shots over time. 

### Post-processing_pipeline

Contains a script for turning the raw class confidences output by the processing pipeline into useable predictions at each taxonomic level. This folder additionally contains helper functions for extracting datetime information from images and size estimates from cropped insects, which can be used as covariates in analyses. 

### Data

Input and output data storage across pipelines. Currently contains a small number of example images and image models. 


