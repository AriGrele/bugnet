extends FileDialog

func toggle():
	if self.visible:self.hide()
	else:self.show()

func _process(_delta):
	var window_size=DisplayServer.window_get_size() #size of entire window
	self.set_size(window_size-Vector2i(14,14)) #keep backgground size of window
	self.set_position(Vector2i(7,7))
	
	if Input.is_action_pressed("escape"):
		self.hide()

func _on_settings_pressed():
	toggle()

func _on_load_pressed():
	toggle()
