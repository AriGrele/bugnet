if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

train.py --data "../../../data/training_data/efficientnet.yaml" --dst "../../../data/models/enet_models" --epochs 100 --img_size 128 --model b0 --str wide --unknown zero --augment