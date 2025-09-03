extends HBoxContainer

var label

func _ready():
	label=get_child(1)

func _process(delta):
	var height=self.get_size().y
	print(height)
	label.add_theme_font_size_override("font_size",height/3)
