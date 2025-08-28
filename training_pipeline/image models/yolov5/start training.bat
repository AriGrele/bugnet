if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
cd yolov5

python train.py --batch 8 --epochs 100 --data "../data/training_data/localizer/yolo.yaml" --imgsz 832 --workers 1 --single-cls --weights yolov5m.pt