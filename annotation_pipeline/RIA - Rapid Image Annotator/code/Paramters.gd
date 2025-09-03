extends TextEdit

var comment
var comments

signal save

func _ready():
	if comments:
		self.set_text(comments)
	self.hide()
	if comment:toggle()

func toggle():
	if self.is_visible():hide()
	else:self.show()

func _on_Paramters_text_changed():
	emit_signal('save')
