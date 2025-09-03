extends Button

func _process(_delta):
	self.set_size(self.get_parent().get_size()) #keep dimensions same as parent
