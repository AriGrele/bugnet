if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
cd yolov5

python detect.py --weights "../../../../data/models/yolo5_m.pt" --iou-thres .25 --source "../../../../data/input" --conf-thres 0.11 --img-size 3200