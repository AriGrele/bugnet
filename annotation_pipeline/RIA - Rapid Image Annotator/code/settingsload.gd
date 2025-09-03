extends FileDialog

var settings

func _ready():
	hide()

func toggle():
	if self.is_visible():hide()
	else:show()

func _process(_delta):
	if Input.is_action_just_pressed("ui_cancel"):
		if self.is_visible():hide()

func _on_load_pressed():
	toggle()
