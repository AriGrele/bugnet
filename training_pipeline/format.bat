if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

format_json_for_models.py --img_src "../data/database_pipeline/good" --dst "../data/training_data" --min_thresh 100 --min_final 0 --max_final 2000 --test_size 10 --enet --img_name