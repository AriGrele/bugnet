extends Node2D

var functions = preload("res://code/functions.gd").new() # directory loading functions
var grid_box = preload("res://code/specimen_photos.tscn") # preload scene for displaying images
var images = []
var grid
var path = ''
var selecting = -1
var state = false
var current_page = 1
var images_per_page = 200
var total_pages = 1
var all_filenames = []
var slider=200

var sorting_data
var filtered_filenames = []
var filter_textedit

var rankreg=RegEx.new()
var taxonreg=RegEx.new()

signal page_changed(page)

func deselect():
	for image in images:
		image.get_child(1).button_pressed=false
			
func click(index,dir):
	index=index
	if dir==-1:
		selecting=index
		state=images[index].get_child(1).button_pressed
		
	if dir==0 and selecting>-1:
		for i in range(min(index,selecting),max(index,selecting)+1):
			images[i].get_child(1).button_pressed=bool(1-int(state))

	if dir==1:
		selecting=-1

func load_page(page):
	images=[]
	current_page = page
	var start_index = (page - 1) * images_per_page
	var end_index = min(start_index + images_per_page, filtered_filenames.size())

	for child in grid.get_children():
		child.free()
	
	var bi=0 #indexing for buttons
	for i in range(start_index, end_index):
		var file = filtered_filenames[i]
		var new_box = grid_box.instantiate() # get new image holder
		var image = new_box.get_child(0).get_child(0) # get color rect shader for displaying image
		var button = new_box.get_child(1)
		
		button.click.connect(click)
		button.set_index(bi)
		bi+=1
		
		image.update_texture(file) # replace texture with one from directory
		
		grid.add_child(new_box) # add to grid
		
		images.append(new_box)
		
		_on_scale_slider_value_changed(slider) #default to 200px wide
		
	var pagelab=get_node('../screen/upper_container/top/buttons/HBoxContainer/TextEdit')
	pagelab.set_text(str(page)+'/'+str(total_pages))
	
	get_node('../modify_data').update_data()

func load_images(new_path=''):
	if new_path != '':
		path = new_path

	images.clear()

	var dir = DirAccess.open(path)
	if dir == null:
		printerr("Error: Unable to open directory at path: " + path)
		return

	all_filenames = functions.dir_contents(path)

	if all_filenames.is_empty():
		printerr("Error: No images found in directory: " + path)
		return

	print(all_filenames.size())
	var file_data = {} # Dictionary to store file data including taxon and size
	sorting_data={}
	var l=all_filenames.size()
	var i=0
	for file in all_filenames:
		i=i+1
		if i%1000==0:
			print(i)
		var file_obj = FileAccess.open(file, FileAccess.READ)
		if file_obj:
			var file_size = file_obj.get_length()
			file_obj.close()
			
			var taxon = get_taxon_from_json(file.get_file())
			
			if not file_data.has(taxon):
				file_data[taxon] = []
			file_data[taxon].append({"file": file, "size": file_size})
			
			var name=taxon.replace('_unknown','').split('_')
			var rank=['#phylum','#class','#order','#family','#genus','#species'][name.size()]
			sorting_data[file.get_file()]={'taxon':taxon,'rank':rank}
		else:
			printerr("Error: Unable to open file: " + file)

	# Sort files within each taxon by size
	for taxon in file_data.keys():
		file_data[taxon].sort_custom(func(a, b): return a["size"] > b["size"])

	# Flatten the sorted structure back into all_filenames
	all_filenames.clear()
	for taxon in file_data.keys():
		for file_info in file_data[taxon]:
			all_filenames.append(file_info["file"])

	filtered_filenames = all_filenames.duplicate()
	apply_filter()

func apply_filter():
	var filter_texts = filter_textedit.get_node('upper/filterbox/taxonform').get_text().to_lower()
	
	if filter_texts.is_empty():
		filtered_filenames = all_filenames.duplicate()
	else:
		filtered_filenames = all_filenames.duplicate()
		for filter_text in filter_texts.split(','):
			for i in range(filtered_filenames.size() - 1, -1, -1):
				var file=filtered_filenames[i]
				var data = sorting_data[file.get_file()]
				if filter_text.begins_with("#"):
					rankreg.compile("(?i)" + filter_text.replace('#',''))
					if not rankreg.search(data['rank']):
						filtered_filenames.remove_at(i)
				else:
					taxonreg.compile("(?i)" + filter_text)
					if not taxonreg.search(data['taxon']):
						filtered_filenames.remove_at(i)

	total_pages = ceil(filtered_filenames.size() / float(images_per_page))
	current_page = 1
	load_page(1)

func update_data(file_path): #assumes just image name
	var taxon = get_taxon_from_json(file_path)
	var name=taxon.replace('_unknown','').split('_')
	var rank=['#phylum','#class','#order','#family','#genus','#species'][name.size()]
	
	sorting_data[file_path]={'taxon':taxon,'rank':rank}

func get_taxon_from_json(file_path):
	var json_path = "local_data/" + file_path + ".json"
	if FileAccess.file_exists(json_path):
		var json = JSON.new()
		var error = json.parse(FileAccess.get_file_as_string(json_path))
		if error == OK:
			var data = json.get_data()
			if data.has("validations"):
				var most_recent = null
				var most_recent_timestamp = 0
				for validator in data["validations"]:
					if data["validations"][validator]["timestamp"] > most_recent_timestamp:
						most_recent = data["validations"][validator]
						most_recent_timestamp = most_recent["timestamp"]
				if most_recent:
					return(most_recent["taxon_name"])
	else:
		return(create_json_for_file(file_path))

func create_json_for_file(file_path):
	var json_path = "local_data/" + file_path.get_file() + ".json"
	var file_name = file_path.get_file()
	var name_parts = file_name.split('_')
	var id = name_parts[-1]
	var conf = name_parts[-2]
	var taxon = "_".join(name_parts.slice(0, -2)).replace('-',' ')
	
	#var data = {
		#"image_id": id,
		#"validations": {
			#"BugNet": {
				#"validator": "BugNet",
				#"timestamp": Time.get_unix_time_from_system(),
				#"taxon_name": taxon,
				#"confirmed": 0}}}
	#
	#var json_string = JSON.stringify(data)
	#var file = FileAccess.open(json_path, FileAccess.WRITE)
	#file.store_string(json_string)
	#file.close()
	
	return(taxon)
	
func _on_next_pressed():
	if current_page < total_pages:
		load_page(current_page + 1)
		page_changed.emit(current_page)

func _on_previous_pressed():
	if current_page > 1:
		load_page(current_page - 1)
		page_changed.emit(current_page)


func _ready():
	grid=get_node('../screen/upper_container/cols/middle/scroll/grid')
	grid.unclick.connect(deselect) #deselect images when clicking outside of them
	
	filter_textedit = get_node("../screen/upper_container/cols/left/options/tabs/Annotate taxa")  # Adjust the path as needed
	filter_textedit.filter.connect(apply_filter)
	
	for child in grid.get_children(): #clear all results when called
		child.queue_free()
		
	if path!='':
		load_images()

func _on_scale_slider_value_changed(value):
	slider=value
	for child in grid.get_children():
		child.set_custom_minimum_size(Vector2(value,value+40))

func _on_file_dialog_dir_selected(dir):
	path=dir
	if path!='':
		load_images()

func _on_go_pressed():
	var pagelab=get_node('../screen/upper_container/top/buttons/HBoxContainer/TextEdit')
	var text = pagelab.get_text().split('/')[0].strip_edges()
	
	if text.is_valid_int():
		var new = int(text)
		if new > 0 and new <= total_pages:
			load_page(new)
			page_changed.emit(current_page)
		else:
			pagelab.set_text(str(current_page) + '/' + str(total_pages))
	else:
		pagelab.set_text(str(current_page) + '/' + str(total_pages))
