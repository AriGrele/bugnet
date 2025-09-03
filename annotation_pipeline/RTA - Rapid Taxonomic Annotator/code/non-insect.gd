extends Button

signal nonbug(text)

func _on_pressed():
	nonbug.emit('Non-insect')
