extends Button

signal hideimg

func _on_pressed():
	hideimg.emit()
	
	if self.get_text()=='Hide valid':
		self.text='Show valid'
	else:
		self.text='Hide valid'

