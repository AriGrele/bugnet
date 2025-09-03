extends OptionButton

func _ready():
	for item in ['Light mode','Dark mode']:
		self.add_item(item)
