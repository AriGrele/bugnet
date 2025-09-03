extends Control

var modes
var settings
var backgrounds

var settingvals

func _ready():
	settingvals=get_node('/root/Main/View/CanvasLayer/Center/Settings')
	settingvals.connect('modechange',self,'changetheme')
	
	modes={'dark':load("res://themes/darktheme.tres"),'light':load("res://themes/lighttheme.tres")}
	backgrounds={'light':Color(0.922,0.922,0.922,1.0),'dark':Color(0.192,0.192,0.192,1.0)}
	settings=get_node('/root/Main/loadsettings').get('settings')
	
	changetheme()
	
func changetheme():
	settings=get_node('/root/Main/loadsettings').get('settings')
	self.set_theme(modes[settings['Mode']['mode']])
	VisualServer.set_default_clear_color(backgrounds[settings['Mode']['mode']])
	update()
