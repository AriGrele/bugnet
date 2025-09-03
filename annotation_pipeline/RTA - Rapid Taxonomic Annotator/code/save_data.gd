extends Node2D

var functions = preload("res://code/functions.gd").new() #directory loading funcitons

var saveform
var grid
var imagedata

func save_data(user):
	var data=imagedata.data
	for img in data:
		if not data[img].has('uri'):
			data[img]['uri']=img
		if not data[img].has('users'):
			data[img]['users']={}
		data[img]['users'][user]=data[img]['taxon_name']
		
		print(data[img])
		functions.save_file(str('local_data/',img,'.json'),data[img])

func _ready():
	saveform=get_node('../screen/upper_container/cols/left/options/tabs/Annotate taxa') #taxonomic annotation scene node
	grid=get_node('../screen/upper_container/cols/middle/scroll/grid')
	imagedata=get_node('../modify_data')
	
	saveform.saved.connect(save_data)
	
	
	
	
	
