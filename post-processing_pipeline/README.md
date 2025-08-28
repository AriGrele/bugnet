#Post-processing of image predictions

##insect_formating.R

Main script for processing cropped insect images and predictions. While the processing pipeline will output a first pass guess for each image, this prediction always applies a 50% confidence threshold and does not take information from multiple images when insects are present in multiple frames. 
This R script aggregates data across all images for an insect, and allows working with raw predictions. 

##Helper scripts

 * grab_dates.bat grabs the datetime exif data from all input images for later analysis
 * grab_pixels.py grabs the pixel area of each insect within a crop for later analysis. This value has been found to correlate well with insect biomass in the literature (R^2 ~= 0.7).
