extends HBoxContainer

signal update
signal remove(item)

var key
var parm

func _ready():
	key  = get_node('./addkey/enterkey')
	parm = get_node('./Parameters')
	key.connect('save',self,'change')
	parm.connect('save',self,'change')

func _on_remove_pressed():
	self.queue_free()
	emit_signal('remove',self)

func change():
	print('change - enterkey text: ',key.get_parent().get_text())
	emit_signal('update')
