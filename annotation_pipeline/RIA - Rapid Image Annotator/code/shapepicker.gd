extends Label

signal shape(type)

func _on_box_pressed():
	emit_signal("shape",'box')

func _on_line_pressed():
	emit_signal("shape",'line')

func _on_circle_pressed():
	emit_signal("shape",'circle')
