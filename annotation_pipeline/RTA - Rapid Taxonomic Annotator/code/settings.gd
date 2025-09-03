extends Node2D

var functions = preload("res://code/functions.gd").new() #directory loading funcitons
var light     = preload("res://themes/lighttheme.tres")
var dark      = preload("res://themes/darktheme.tres")

var settings
var gui
var image_grid
var textform

# Define default settings
var default_settings = {
	'display': {'mode': 0},
	'interface': {'language': 0},
	'misc':{
		'version':"unknown",
		'name':'default',
		'image_path': '',
		'current_page': 1}}

func update():
	set_theme(settings['display']['mode'])
	set_language(settings['interface']['language'])
	set_image_path(settings['misc']['image_path'])
	set_current_page(settings['misc']['current_page'])
	set_val_name(settings['misc']['name'])

func set_val_name(text):
	textform.set_text(text)

func set_image_path(path):
	if path and path != '':
		image_grid.path = path
		image_grid.load_images()

func set_current_page(index):
	image_grid.load_page(index)

func set_theme(mode):
	var screen=get_node('../screen')
	screen.set_theme([light,dark][mode])

func set_language(_language):pass

func save_settings():
	functions.save_file('data/settings.json', settings)

func ensure_default_settings():
	var changed = false
	for category in default_settings:
		if category not in settings:
			settings[category] = {}
			changed = true
		for key in default_settings[category]:
			if not settings[category].has(key):
				settings[category][key] = default_settings[category][key]
				changed = true
	if changed:
		save_settings()
	
		
func _ready():
	settings=functions.load_file('data/settings.json')
	if not settings: #if no settings file
		settings = default_settings.duplicate(true)		
		save_settings()
	else:
		ensure_default_settings()
		
	gui=get_node('../screen/settings/hadj/vadj/settings_background/cols')
	image_grid = get_node('../display_images')
	image_grid.page_changed.connect(_on_page_changed)
	
	textform=get_node('../screen/upper_container/cols/left/options/tabs/Annotate taxa')
	textform=textform.get_node('lower/saveform/nameform')
	textform.nameform.connect(name_changed)
	
	var children=gui.get_children()
	var cols={}
		
	for col in children: #update settings gui
		cols[col.name]={}
		for row in col.get_children():
			cols[col.name][row.name]=row
		
	for col in settings:
		for row in settings[col]:
			if not row in ['current_page','image_path','name','version']:
				cols[col][row].select(settings[col][row])
	
	update()

func _on_mode_item_selected(index):
	settings['display']['mode']=index
	functions.save_file('data/settings.json',settings)
	set_theme(settings['display']['mode'])

func _on_language_item_selected(index):
	settings['interface']['language']=index
	functions.save_file('data/settings.json',settings)
	set_language(settings['interface']['language'])

func update_image_path(path):
	settings['misc']['image_path'] = path
	save_settings()

func update_current_page(page):
	settings['misc']['current_page'] = page
	save_settings()

func _on_file_dialog_dir_selected(dir):
	update_image_path(dir)
	set_image_path(dir)

func _on_page_changed(page):
	update_current_page(page)

func name_changed(text):
	settings['misc']['name'] = text
	save_settings()
