extends Panel

func toggle():
	if self.is_visible():hide()
	else:show()
	
func _ready():pass#hide()

func _on_stats_pressed():toggle()
