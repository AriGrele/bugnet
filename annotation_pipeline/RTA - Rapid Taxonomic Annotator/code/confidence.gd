extends TextEdit

signal confform(text)

func _on_text_changed():
	confform.emit(self.get_text())
