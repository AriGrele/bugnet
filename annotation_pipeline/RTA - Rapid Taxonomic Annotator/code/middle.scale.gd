extends HBoxContainer

func _ready():pass 

func _process(_delta):
	var window_size=DisplayServer.window_get_size() #size of entire window
	self.set_stretch_ratio(window_size.x-402) #Allows this section of hbox to scale dynamically while right and left panels stay 200px
