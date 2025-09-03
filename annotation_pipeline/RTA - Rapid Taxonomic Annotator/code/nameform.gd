extends TextEdit

signal nameform(text)

func _on_text_changed():
	nameform.emit(self.get_text())
