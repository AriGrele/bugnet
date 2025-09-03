extends Container

func _ready():pass 

func _process(delta):
	print(self.get_parent().get_size())
	self.set_size(self.get_parent().get_size())
