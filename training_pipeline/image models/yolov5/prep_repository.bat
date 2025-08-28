if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt