extends FileDialog

var settings

func _ready():
	hide()
	settings=get_node('../Settings')

func _on_FileDialog_dir_selected(dir):
	print(dir)

func _on_load_button_down():toggle()

func toggle():
	if self.is_visible():hide()
	elif not settings.is_visible():show()

func _process(_delta):
	if Input.is_action_just_pressed("ui_cancel"):
		if self.is_visible():hide()




