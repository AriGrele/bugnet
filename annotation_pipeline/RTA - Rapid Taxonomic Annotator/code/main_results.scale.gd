extends HBoxContainer

var full_name=''
signal taxonpress(taxon)

func _process(_delta):
	self.set_size(self.get_parent().get_size()-Vector2(0,8)) #keep dimensions same as parent
	self.set_position(Vector2(4,4))

func _on_button_pressed():
	taxonpress.emit(self.get_child(2).full_name)
