extends VBoxContainer

var data
var key
var enter
var fun
var savedata
var commentdata
var lower

var keys=[]

var regex

signal output()
signal loadkeys(text)

var comment
var comments

func _ready():
	regex=RegEx.new()
	regex.compile("[A-Z]+_[A-Z]+")
	
	savedata={}
	commentdata={}
	lower=get_node('./lower')
	fun=get_node('./function')
	fun.set_text(data[0])
	
	comment=(data[0]=='Comments')
	
	for k in comments['Comments'].keys():
		commentdata[k.as_text()]=comments['Comments'][k]
	print(data)
	for item in data[1]:
		newnode(item,comment)
		emit_signal('loadkeys',item)
	savedata={data[0]:data[1]}

func remove(item):
	keys.erase(item)
	save()

func save():
	savedata={data[0]:[]}
	commentdata={data[0]:{}}
	for k in keys:
		print('k in keys: ',k)
		var value=k.get_node('./addkey').get('input')
		print('value: ',value)
		savedata[data[0]].append(value)
		if comment:
			commentdata[data[0]][value]=k.get_node('./Parameters').get_text()
	print('savedata: ',savedata)
	print('-----')
	print('commentdata: ',commentdata)

	emit_signal('output')

func newnode(d,com):
	print(d,' ',com)
	var newkey=load('res://code/keys.tscn').instance()
	
	newkey.connect('update',self,'save')
	newkey.connect('remove',self,'remove')
	
	var text=d
	if typeof(d)!=TYPE_STRING:
		text=d.as_text()
	var caps=regex.search(text)
	if caps!=null:text=caps.get_string().to_lower()
	
	newkey.get_node('./addkey').set_text(text)
	newkey.get_node('./addkey').set('input',d)
	newkey.get_node('./Parameters').set('comment',com)
	
	if str(d)!='New key':
		if d.as_text() in commentdata.keys():
			newkey.get_node('./Parameters').set('comments',commentdata[d.as_text()])
	else:newkey.get_node('./Parameters').set('comments','')
	
	self.add_child(newkey)
	self.move_child(lower,self.get_child_count())
	keys.append(newkey)
	return(newkey)

func _on_add_pressed():
	newnode('New key',comment)
