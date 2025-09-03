extends Button

signal click(index,direction)
var index

func _ready():
	pass#index=self.get_parent().get_index()

func _process(_delta):
	self.set_custom_minimum_size(self.get_parent().get_size()) #keep dimensions same as parent

func _on_button_down():
	click.emit(index,-1)

func _on_mouse_entered():
	click.emit(index,0)
	
func _on_button_up():
	click.emit(index,1)

func set_index(new_index):
	index = new_index
