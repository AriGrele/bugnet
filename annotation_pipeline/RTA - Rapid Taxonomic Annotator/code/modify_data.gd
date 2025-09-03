extends Node2D

var functions = preload("res://code/functions.gd").new() #directory loading funcitons

var grid
var textform
var images
var data
var hidden_confirmed = false
var hidden_images = []

func _ready():
	textform=get_node('../screen/upper_container/cols/left/options/tabs/Annotate taxa') #taxonomic annotation scene node
	textform.applied.connect(apply_names) #connect to updated signal such that when text entered in form the db search will be run
	textform.copied.connect(copy_names)
	
	textform.get_node('lower/saveform/confirm').confirm.connect(confirm_selected)
	textform.get_node('lower/options/confirm').confirm.connect(confirm_all)
	textform.get_node('lower/options/hide').hideimg.connect(toggle_confirmed_visibility)
	textform.get_node('lower/options/non-insect').nonbug.connect(apply_names)
	
	update_data()

func update_data():
	
	data={}	
	grid=get_node('../screen/upper_container/cols/middle/scroll/grid')
	images=grid.get_children()
	
	var local_data=[]
	for item in functions.dir_contents('local_data'):
		local_data.append(item.replace('local_data/','').replace('.json',''))

	for img in images:
		var slice=img.get_child(0).get_child(0).filename.split('/')
		var uri=slice[len(slice)-1]

		if uri in local_data:
			data[uri]=functions.load_file(str('local_data/',uri,'.json'))
			data[uri]['object']=img
		else:
			var name=uri.split('_')
			var id=name[name.size()-1]
			var conf=name[name.size()-2]
			var taxon=name.slice(0,(name.size()-2))
			
			data[uri]={'object':img,
			'image_id':id,
			'validations':{
				'BugNet':{
					'validator': 'BugNet',
					'timestamp': 1,
					'taxon_name': '_'.join(taxon).replace('-',' '),
					'confirmed': 0,
					'conf':conf}}}
				
			save_data(uri)
	
	update_images()

func copy_names():
	#update_data()
	
	for image in images:
		if image.get_child(1).button_pressed and not image in hidden_images:
			var text=image.get_child(0).get_child(2).get_text().get_slice('\n',1)
			textform.get_node('upper/searchbox/taxonform').set_text(text)
			get_node('../parse_taxa').parse_search(text)
			
			break

func update_images():
	hidden_images.clear()
	var display=get_node('../display_images')
	
	for file in data:
		display.update_data(file) #updating name for sorting
		
		var image_obj = data[file]['object']
		var label = image_obj.get_child(0).get_child(0) #taxon label text
		if data[file].has('validations'):
			# Find the most recent validation
			var most_recent = null
			var most_recent_timestamp = 0
			for validator in data[file]['validations']:
				if data[file]['validations'][validator]['timestamp'] > most_recent_timestamp:
					most_recent = data[file]['validations'][validator]
					most_recent_timestamp = most_recent['timestamp']
			
			if most_recent:
				var name=most_recent['taxon_name'].replace('_unknown','').split('_')
				label.update_text(name[name.size()-1],most_recent['taxon_name'].replace('_unknown',''))
				
				image_obj.get_node('image_vbox/taxon_pic').confirm(most_recent['confirmed'])
				if hidden_confirmed and most_recent['confirmed'] == 1:
					image_obj.visible = false
					hidden_images.append(image_obj)
				else:
					image_obj.visible = true
			else:
				label.update_text("Unknown",'')
				image_obj.get_node('image_vbox/taxon_pic').confirm(false)
				image_obj.visible = true
		else:
			label.update_text("Unknown",'')
			image_obj.get_node('image_vbox/taxon_pic').confirm(false)
			image_obj.visible = true
			

func apply_names(text):
	var validator = textform.get_node('lower/saveform/nameform').get_text()
	if validator=='': validator='Default'
	
	var confidence = textform.get_node('lower/saveform/confidence').get_text()
	if confidence=='': confidence=95
	
	var timestamp = Time.get_unix_time_from_system()
	
	for file in data:
		if data[file]['object'].get_child(1).button_pressed and not data[file]['object'] in hidden_images:
			var new_validation = {
				'validator': validator,
				'timestamp': timestamp,
				'taxon_name': text,
				'confirmed': 0,
				'conf':confidence}
			
			if not data[file].has('validations'):
				data[file]['validations'] = {}
				
			data[file]['validations'][validator] = new_validation
			
			functions.save_file(str('local_data/', file, '.json'), data[file])
	
	update_images()

func confirm_selected():
	var validator = textform.get_node('lower/saveform/nameform').get_text()
	if validator=='': validator='Default'
	for file in data:
		if data[file]['object'].get_child(1).button_pressed and not data[file]['object'] in hidden_images:
			toggle_confirmation(file,validator)
	update_images()

func confirm_all():
	var validator = textform.get_node('lower/saveform/nameform').get_text()
	if validator=='': validator='Default'
	
	for file in data:
		if not data[file]['object'] in hidden_images:
			toggle_confirmation(file,validator)
	update_images()

func toggle_confirmation(file,validator):
	if data[file].has('validations') and not data[file]['validations'].is_empty():
		var most_recent = null
		var most_recent_timestamp = 0
		for val in data[file]['validations']:
			if data[file]['validations'][val]['timestamp'] > most_recent_timestamp:
				most_recent = data[file]['validations'][val]
				most_recent_timestamp = most_recent['timestamp']
		
		if most_recent:
			data[file]['validations'][validator]={
					'validator': validator,
					'timestamp': Time.get_unix_time_from_system(),
					'taxon_name': most_recent['taxon_name'],
					'confirmed': 1-most_recent['confirmed'],
					'conf':most_recent['conf']}
		else:
			data[file]['validations'][validator]={
					'validator': validator,
					'timestamp': Time.get_unix_time_from_system(),
					'taxon_name': 'unkown',
					'confirmed': 1,
					'conf':95}
					
		save_data(file)

func save_data(file):
	functions.save_file(str('local_data/', file, '.json'), data[file])

func toggle_confirmed_visibility():
	hidden_confirmed = not hidden_confirmed
	update_images()

func _process(_delta):
	if Input.is_action_just_pressed("save_img"):
		for image in images:
			if image.get_child(1).button_pressed and not image in hidden_images:
				var filename=image.get_node('image_vbox/taxon_pic').filename
				var text=image.get_node('image_vbox/taxon_pic').fullname
				var name=filename.get_file().split('_')
				
				var dir = DirAccess.open("user://")
				var error = dir.copy_absolute(filename, "saved_images/" + text+'_'+name[name.size()-1])
				if error == OK: print("Image saved")
				else: print("Failed to save image")
