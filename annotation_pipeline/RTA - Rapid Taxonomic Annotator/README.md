# Rapid Taxonomic Annotator

This folder contains files associated with version 1.2.10 of the Rapid Taxonomic Annotator

## Using the taxonomic annotator:
After downloading the entire RTA folder, run Rapid Taxonomic Annotator.exe
Load an image directory using the “load image directory” button. Although folders containing any number of images can be loaded, you may experience very long loading times on folders of >10,000 images on some systems. E.g. loading a directory of 250,000 images takes ~20 minutes on the 2023 consumer laptop this readme is being written on. Some data is cached after the first load, so this time may be reduced on subsequent uses of the application.  
Images are assumed to have taxonomic information in their file names in the format of order_family_genus_species, which can be used to filter the loaded images. Note that images can still be loaded without this formating, but some features will be unavailable until images are manually annotated. 

To use, click and drag from image icon to icon to select or deselect images. use the "Add a taxonomic identification" search field to pull taxon names from the GBIF backbone, and apply them to the selected images. 
Additionally, text in this search field prefaced with an octothorpe (e.g. #morphospecies-1) can be applied directly to images even if it does not match a taxon in the GBIF backbone.

Images can be filtered to specific taxa using the "filter images by taxon" search field. Additionally, images can be filtered to specific taxonomic levels using the text #order, #family, etc. These searches can be concatenated using commas, e.g. "lepidoptera, #genus" will filter to images which have a genus level ID and are in the order Lepidoptera.

Annotated image data will be stored locally, but will not be saved until confirmed, either by hitting the "confirm" button to confirm selected images or "confirm all" to confirm all currently displayed images. Additionally, all annotation data can be saved by pressing "save annotations" in the upper toolbar.
Annotations will be saved as a separate json for each image under the "local_data" folder, with data of the original ID if available, taxonomic annotation, datetime of annotation, and if entered annotator name and confidence level. 

Additionally, pressing CTRL + S will save a copy of all currently selected images to the "saved_images" folder.

## Version 2.6.10
### License: GNU Affero General Public License v3.0 (2025)
