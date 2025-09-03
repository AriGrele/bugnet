extends VBoxContainer

var settings
var keys
var comments
var scroll
var items

signal output

func _ready():
	for n in self.get_children():
		self.remove_child(n)
		n.queue_free()
	
	var loadsettings=get_node('/root/Main/loadsettings')
	settings=loadsettings.get('settings')
	loadsettings.connect('reset',self,'_ready')
	
	keys=settings['Controls']['controls']
	comments=settings['Comments']['comments']
	items=spawn(keys,comments)

func newnode(k,d,com):
	var controlpicker=load('res://code/controlpicker.tscn').instance()
	controlpicker.get_node('.').set('data',[k,d[k]])
	controlpicker.get_node('.').set('comments',com)
	controlpicker.get_node('.').set_scale(Vector2(.5,.5))
	controlpicker.get_node('.').connect('output',self,'savedata')

	self.add_child(controlpicker)
	return(controlpicker)

func spawn(data,com):
	var nodes=[]
	for key in data:nodes.append(newnode(key,data,com))
	return(nodes)

func remove():
	items[-1].queue_free()
	items.erase(items[-1])

func _on_addnew_pressed():
	items.append(newnode('newkey',{'newkey':['']},comments))

func _on_remove_pressed():
	remove()

func savedata():
	keys={}
	comments={}
	for child in self.get_children():
		var save=child.get_node('.').get('savedata')
		var com=child.get_node('.').get('commentdata')
		
		
		for k in save.keys():keys[k]=save[k]
		if child.get_node('.').get('comment'):
			for k in com.keys():comments[k]=com[k]
	
	
	emit_signal('output')
	
	

