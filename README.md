\# BugNet data pipeline

These folders contain scripts and a small number of trained models for creating training datasets, training, and deploying BugNet models.
There are additionally example batch files in each folder demonstrating the creation from scratch of a small classification model. See

* database\_pipeline/scrape\_images.bat
* training\_pipeline/format.bat
* training\_pipeline/image models/Efficientnet/Train.bat
* processing\_pipeline/run.bat

Running these files with the current parameters will produce a dataset of ~13,000 images of Lepidoptera, format these data for training a classification model, train a classification model with ~28 species, and use this model to classify insects in an example camera trap image.

\## Folders
### Database\_pipeline

