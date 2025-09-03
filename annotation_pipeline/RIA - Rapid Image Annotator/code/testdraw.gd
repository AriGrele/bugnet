extends Panel

var sel='none'
var cols

var picker
var panel

var settings

func _ready():
	picker=get_node('../Container/colormanager')
	panel=get_node('..')
	
	var loadsettings=get_node('/root/Main/loadsettings')
	settings=loadsettings.get('settings')
	loadsettings.connect('reset',self,'_ready')
	
	cols={'outer':settings['Color']['outer'],'inner':settings['Color']['inner'],'fill':settings['Color']['fill'],'lines':settings['Color']['lines']}

func _process(_delta):update()

func _draw():
	draw_rect(Rect2(Vector2(20,20),Vector2(230,230)),cols['fill']) #fill
	draw_rect(Rect2(Vector2(20,20),Vector2(230,230)),cols['outer'],false,2) #outer
	draw_rect(Rect2(Vector2(22,22),Vector2(226,226)),cols['inner'],false,2) #inner
	
	draw_line(Vector2(140,250),Vector2(140,500),cols['lines'])
	draw_line(Vector2(20,375),Vector2(250,375),cols['lines'])


func _on_outer_pressed():
	panel.show()
	sel='outer'
	picker.set_pick_color(cols[sel])

func _on_inner_pressed():
	panel.show()
	sel='inner'
	picker.set_pick_color(cols[sel])

func _on_fill_pressed():
	panel.show()
	sel='fill'
	picker.set_pick_color(cols[sel])

func _on_lines_pressed():
	panel.show()
	sel='lines'
	picker.set_pick_color(cols[sel])

func _on_colormanager_color_changed(color):
	if sel!='none':
		cols[sel]=color

func _on_savecolor_pressed():
	sel='none'
	panel.hide()
