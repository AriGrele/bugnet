extends ColorPicker

var col
var sel=null

func toggle(n):
	sel=n
	if self.is_visible():hide()
	else:show()


func _on_outer_pressed():toggle(0)


func _on_inner_pressed():toggle(1)


func _on_fill_pressed():toggle(2)


func _on_lines_pressed():toggle(3)


func _on_colormanager_preset_added(color):
	print(sel)
	toggle(null)
