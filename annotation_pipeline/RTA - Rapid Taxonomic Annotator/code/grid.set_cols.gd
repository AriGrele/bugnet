extends GridContainer

signal unclick

func _process(_delta):
	var child=self.get_children()
	if len(child)>0: #skipped when no children
		child=child[0]
		var child_size=child.get_size().x+20 #x+20 = x dimension + margin of 20 pixels in container
		var window_size=DisplayServer.window_get_size() #size of entire window
		
		self.set_columns(clamp(floor((window_size.x-402)/child_size),1,100000)) #for given size of image, change number of columns to fit window width

func _on_gui_input(event):
	if event.is_action_pressed('left_mouse'):
		unclick.emit()
