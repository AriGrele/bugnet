extends FileDialog

var settings

func _ready():
	hide()

func _on_FileDialog_dir_selected(dir):
	print(dir)

func toggle():
	if self.is_visible():hide()
	else:show()

func _on_setcontrols_pressed():toggle()

func _process(_delta):
	if Input.is_action_just_pressed("ui_cancel"):
		if self.is_visible():hide()
