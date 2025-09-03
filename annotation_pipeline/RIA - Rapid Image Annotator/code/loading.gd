extends Label

var alpha=0
var spool=0
var nav
var loadstate

func _ready():
	nav=get_node('..')

func _process(delta):
	loadstate=nav.get('loadstate')
	alpha+=delta
	if loadstate==0:spool-=delta
	else:spool+=delta
	spool=clamp(spool,0,1)
	print((.5+.5*sin(alpha*2))*spool)
	
	modulate.a=(.5+.5*sin(alpha*2))*spool
