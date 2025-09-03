extends HBoxContainer

var parent

func _ready():
	parent=self.get_parent()

func _process(_delta):
	var dim=parent.get_size() #size of entire window
	self.set_size(dim) #keep backgground size of window
