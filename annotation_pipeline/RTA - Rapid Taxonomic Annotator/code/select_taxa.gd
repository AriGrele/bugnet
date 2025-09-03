extends VBoxContainer

var result_text=preload("res://code/result_text.tscn") #preload scene for displaying results text
var functions = preload("res://code/functions.gd").new() # directory loading functions

signal updated(new_text) #signal to emit when search entered
signal applied(set_text) #signal to apply text to selected images
signal copied
signal saved(user) 
signal filter(text)

var textform #for holding search bar object
var result_list #for holding results text object
var full_name=''

var taxon_img=[]

func setsearch(text):
	var name=text.replace('_unknown','').split('_')
	textform.set_text(name[name.size()-1]) #set text to full name returned by search
	full_name=text
	updated.emit('') #clear search
	
	_on_new_img_pressed()

func _ready():
	textform = get_node('upper/searchbox/taxonform') #get nodes within scene
	result_list  = get_node('upper/resultsbox/scroll/results_box/results')
	
	self.set_custom_minimum_size(Vector2(0,0))
	
	var dir_contents = functions.dir_contents('assets/example_taxa')
	for f in dir_contents:
		if '.jpg' in f.to_lower():
			taxon_img.append(f)

func _on_taxonform_text_changed():
	updated.emit(textform.get_text()) #emit updated signal when text changed in search bar

func create_labels(results):
	if len(results)<1:
		get_node('upper/resultsbox').hide()
		get_node('upper/comparison').show()
	else:
		get_node('upper/resultsbox').show()
		get_node('upper/comparison').hide()
		
	for child in result_list.get_children(): #clear all results when called
		child.queue_free()
	
	for result in results: #for each result returned by sql search:
		var fullname=result['full_name']
		var uri=result['uri']
		var output=str(result['taxon'],'\n[i]',result['group'].to_pascal_case(),'[/i]') #format to display taxonomic rank and name
		
		var new_result=result_text.instantiate() #get new label for results text
		
		new_result.get_child(0).taxonpress.connect(setsearch)
		new_result.get_child(1).tooltip_text = fullname.replace('_unknown','').replace('_','\n')
		
		var label = new_result.get_child(0).get_child(2) #label object
		var icon  = new_result.get_child(0).get_child(0) #texturerect object
		
		label.set_text(output) #add text
		label.full_name=fullname
		icon.set_texture(load(str('res://assets/taxon_thumbs/',uri)))
		
		result_list.add_child(new_result) #add to vbox

func _on_apply_pressed():
	if '#' in textform.get_text():
		applied.emit(textform.get_text())
	else:
		applied.emit(full_name)

func _on_copy_pressed():
	copied.emit()

func _on_save_pressed():
	var user=get_node('lower/saveform/nameform')
	saved.emit(user.get_text())

func _on_filter_pressed():
	filter.emit()

func _on_clear_pressed():
	self.get_node('upper/filterbox/taxonform').set_text('')
	filter.emit()

func _on_new_img_pressed():
	var search_name = '_'.join(full_name.split('_').slice(1)).replace('_unknown','').replace(' ','-')
	
	var matching_images = []
	for img in taxon_img:
		if search_name.to_lower() in img.to_lower():
			matching_images.append(img)
	
	if matching_images.size() > 0:
		# Randomly choose one image
		var rng = RandomNumberGenerator.new()
		rng.randomize()
		var random_index = rng.randi_range(0, matching_images.size() - 1)
		var chosen_image = matching_images[random_index]
		
		print(chosen_image)
		get_node('upper/comparison/VBoxContainer/taxon_img').update_texture(chosen_image)
	
	else:
		get_node('upper/comparison/VBoxContainer/taxon_img').update_texture('')
