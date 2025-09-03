extends Button

signal confirm

func _on_pressed():
	confirm.emit()
