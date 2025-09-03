extends Label

func _process(_delta):
	self.set_text(str('FPS: ',Engine.get_frames_per_second()))
