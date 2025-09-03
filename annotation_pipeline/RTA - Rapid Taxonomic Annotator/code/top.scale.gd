extends Control

func _process(_delta):
	var window_size=DisplayServer.window_get_size() #size of entire window
	self.set_size(Vector2(window_size.x,40)) #set x dim to width, y dim to 40px
