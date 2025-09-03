extends Node2D

func _process(delta):
	var window_size = DisplayServer.window_get_size()  # size of entire window
	var reference_size = Vector2i(1200, 700)  # reference size for scale 1
	
	# Calculate scale based on the smaller dimension ratio
	var scale_x = float(window_size.x) / float(reference_size.x)
	var scale_y = float(window_size.y) / float(reference_size.y)
	var new_scale = min(scale_x, scale_y)
	
	self.scale = Vector2(new_scale, new_scale)
	self.position = Vector2i(window_size.x / 2, window_size.y / 2)
