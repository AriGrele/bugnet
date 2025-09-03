extends VBoxContainer

var popup
var key
var main

var funs

signal save

func loadfun(ev):
	var text=ev.as_text()
	if text!='':
		var desc=Label.new()
		desc.set_text(text)
		self.add_child(desc)
		funs.append(text)

func addfun(id):
	
	var text=popup.get_popup().get_item_text(id)
	
	if text!='Remove function':
		var desc=Label.new()
		desc.set_text(text)
		self.add_child(desc)
		funs.append(text)
	elif len(funs)>0:
		self.get_children()[-1].queue_free()
		funs.erase(funs[-1])

	emit_signal('save')

func _ready():
	funs=[]
	main=get_node('..')
	main.connect('loadkeys',self,'loadfun')
