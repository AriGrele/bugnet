extends Panel

func _process(_delta):
	var window_size=DisplayServer.window_get_size() #size of entire window
	self.set_size(window_size) #keep backgground size of window

