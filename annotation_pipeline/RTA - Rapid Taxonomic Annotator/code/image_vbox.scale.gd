extends VBoxContainer

func _process(_delta):
	var parent_size=self.get_parent().get_custom_minimum_size()
	self.set_custom_minimum_size(parent_size) #keep dimensions same as parent
