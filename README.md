# BugNet data pipeline

These folders contain scripts and a small number of trained models for creating training datasets, training, and deploying BugNet models.
There are additionally example batch files in each folder demonstrating the creation from scratch of a small classification model. See

* database_pipeline/scrape_images.bat
* training_pipeline/format.bat
* training_pipeline/image models/Efficientnet/Train.bat
* processing_pipeline/run.bat

Running these files with the current parameters will produce a dataset of ~13,000 images of Lepidoptera, format these data for training a classification model, train a classification model with ~28 species, and use this model to classify insects in an example camera trap image.

## Folders
### Database_pipeline

