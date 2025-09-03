extends Panel

var filedialog
var datadialog
var colors

var names
var mode
var select
var datadir
var testdraw
var cols
var controls
var contkeys

signal savesettings
signal modechange
signal selectchange(selection)

var settings

var comments

var map={"Top margin up":'tmu',"Top margin down":'tmd',"Right margin right":'rmr',"Right margin left":'rml',"Bottom margin up":'bmu',"Bottom margin down":'bmd',"Left margin right":'lmr',"Left margin left":'lml'}

func update_input():
	contkeys=controls.get('keys')
	comments=controls.get('comments')
	
	for item in map:
		InputMap.action_erase_events(map[item])
		if item in contkeys.keys():
			for k in contkeys[item]:
				InputMap.action_add_event(map[item],k)

func reset():
	var loadsettings=get_node('/root/Main/loadsettings')
	settings=loadsettings.get('settings')
	mode=settings['Mode']['mode']
	select=settings['Select']['select']
	get_node('deselect').set_pressed_no_signal(select)
	cols=settings['Color']
	update_input()
	emit_signal('modechange')
	
func _ready():
	hide()
	filedialog=get_node('../ImageLoad')
	datadialog=get_node("DataLoad")
	colors=get_node("margin/ColorPanel")
	testdraw=get_node("margin/ColorPanel/testdraw")
	controls=get_node("controls/scroll/keys")
	controls.connect('output',self,'savecont')
	
	update_input()
	
	var loadsettings=get_node('/root/Main/loadsettings')
	settings=loadsettings.get('settings')
	loadsettings.connect('reset',self,'reset')
	
	select=settings['Select']['select']
	get_node('deselect').set_pressed_no_signal(select)
	
	cols=testdraw.get('cols')
	mode=settings['Mode']['mode']

func _on_settings_pressed():toggle()
func _on_save_pressed():toggle()

func toggle():
	if self.is_visible():
		hide()
		colors.hide()
		contkeys=controls.get('keys')
		emit_signal("savesettings")

	elif not filedialog.is_visible() and not datadialog.is_visible():show()

func _process(_delta):
	if Input.is_action_just_pressed("ui_cancel"):toggle()

func _on_darkmode_pressed():
	mode='dark'
	emit_signal("savesettings")
	emit_signal('modechange')

func _on_lightmode_pressed():
	mode='light'
	emit_signal("savesettings")
	emit_signal('modechange')

func _on_savecolor_pressed():
	cols=testdraw.get('cols')
	emit_signal("savesettings")

func _on_DataLoad_dir_selected(dir):
	datadir=dir
	emit_signal("savesettings")

func _on_DataLoad_file_selected(path):
	datadir=path
	emit_signal("savesettings")

func savecont():
	update_input()
	emit_signal('savesettings')

func _on_deselect_toggled(button_pressed):
	select=button_pressed
	emit_signal("savesettings")
	emit_signal('selectchange',button_pressed)
