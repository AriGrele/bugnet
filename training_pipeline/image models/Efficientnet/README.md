#EfficientNet training

##train.py

Main python script for training new classification models. Takes input from a formated yaml file produced using "format_json_for_models.py" in the above directory.

##Example useage:

```
train.py --data "../../../data/training_data/classifier/efficientnet.yaml" --dst "../../../data/models/enet_models" --epochs 100 --img_size 128 --model b3 --str wide --unknown zero --augment
```

Which will train a classification model based on the data in efficientnet.yaml for 100 epochs, at an image resolution of 128 x 128 pixels, applying image augmentation during training, and using the EfficentNet B3 model (weakest = B0, strongest = B7). The str and unknown arguments direct the script to use a specific strategy for dealing with hierarchical data and unlabled images, here predicting all taxonomic levels in parallel and attempting to output zeros for every class when predicting an unknown insect. 

##arguments

```
data     - Path to yaml data file
img_size - image resolution
model    - Efficientnet model architecture (B0 - B7)
dst      - folder to save model weights
epochs   - number of training epochs
weights  - starting weights
str      - hierarchy structure; one of: flat, simple, wide, funnel, pyramid, or full
unknown  - method of calculating loss for unknowns; one of: classes, subclasses, zero, random, subrandom, uniform, subuniform, or ignore
augment  - apply image augmentation when training

```

