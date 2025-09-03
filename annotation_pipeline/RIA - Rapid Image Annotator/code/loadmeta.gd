extends Node2D

var info

func _ready():
	info=load_data('res://data/info.cfg')

func load_data(path):
	var data={}
	var config=ConfigFile.new()

	var err=config.load(path)
	if err != OK:return
	
	for item in config.get_sections():
		data[item]={}
		for key in config.get_section_keys(item):
			data[item][key]=config.get_value(item,key)
	return(data)


