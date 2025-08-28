if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

process_images.py --images "../data/input" --yolo_weights "../data/models/yolo5_m.pt" --enet_weights "../data/models/enet_models/best_model.pt" --dst "../data/output" --resolution 3200 --filter "../data/models/binary_filter.4.pt" --static --crop