# YOLOv5 Training
This folder includes some helper batch files for training YOLO models.

prep_repository.bat - clones the YOLOv5 github repository to this folder and installs requirements. NB while YOLOv5 models can be trained via the more modern Ultralytics python library, the version 5 models included in that library are not the same as those from the original github, and typically underperform (they do run much faster though, if your use case can handle the tradeoff.)

start_training.bat - train a new model. See yolov5/train.py or the Ultralytics website for a complete list of parameters

detect.bat - process images and predict bounding boxes

