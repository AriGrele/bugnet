extends Node2D

var settings
var settingvals
var nav
var controls

signal imgchange
signal annchange
signal reset

var settings_path

func _ready():
	var defaults=load_data('res://data/defaults.cfg')
	settings_path=defaults['Settings']['path']
	settings=load_data(settings_path)
	var directory = Directory.new()
	
	if settings['Dirs']['images'] == '' or not directory.dir_exists(settings['Dirs']['images']):
		settings['Dirs']['images'] = 'data/images'
	if settings['Dirs']['data'] == '' or not directory.file_exists(settings['Dirs']['data']):
		settings['Dirs']['data']   = 'data/annotations.json'
	
	nav         = get_node('/root/Main/ImageNav')
	settingvals = get_node('/root/Main/View/CanvasLayer/Center/Settings')
	controls    = get_node('/root/Main/View/CanvasLayer/Center/Settings/controls/scroll/keys')
	
	settingvals.connect('savesettings',self,'save_all')
	nav.connect('savebox',self,'save_all')
	
func load_data(path):
	var data={}
	var config=ConfigFile.new()

	var err=config.load(path)
	if err != OK:return(load_data('res://data/defaults.cfg'))
	
	for item in config.get_sections():
		data[item]={}
		for key in config.get_section_keys(item):
			data[item][key]=config.get_value(item,key)
	return(data)

func save_data(data,path):
	var config=ConfigFile.new()
	for key in data.keys():
		for item in data[key].keys():
			config.set_value(key,item,data[key][item])
	config.save(path)

func reset_data():
	settings=load_data('res://data/defaults.cfg')
	save_data(settings,settings_path)
	emit_signal('reset')

func save_all():
	settings['Mode']['mode']         = settingvals.get('mode')
	settings['Color']['outer']       = settingvals.get('cols')['outer']
	settings['Color']['inner']       = settingvals.get('cols')['inner']
	settings['Color']['fill']        = settingvals.get('cols')['fill']
	settings['Color']['lines']       = settingvals.get('cols')['lines']
	settings['Controls']['controls'] = controls.get('keys')
	settings['Images']['index']      = nav.get('index')
	settings['Comments']['comments'] = settingvals.get('comments')
	settings['Select']['select']     = settingvals.get('select')
	
	save_data(settings,settings_path)
	
func _on_ImageLoad_dir_selected(dir):
	settings['Dirs']['images']=dir
	save_data(settings,settings_path)
	emit_signal("imgchange")

func _on_DataLoad_file_selected(path):
	settings['Dirs']['data']=path
	save_data(settings,settings_path)
	emit_signal("annchange")

func _on_reset_pressed():reset_data()

func _on_settingsload_file_selected(path):
	settings_path=path
	
	var defaults=load_data('res://data/defaults.cfg')
	defaults['Settings']['path']=settings_path
	save_data(defaults,'res://data/defaults.cfg')
	
	settings=load_data(settings_path)
	save_data(settings,settings_path)
	emit_signal('reset')
