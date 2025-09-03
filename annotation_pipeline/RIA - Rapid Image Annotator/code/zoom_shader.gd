extends ColorRect

var pos
var vpos
var uv
var mat
var panel
var nav
var parent

func toggle():
	if self.is_visible():
		hide()
	else:show()

func _ready():
	self.hide()
	
	parent = self.get_parent()
	nav=get_node('/root/Main/ImageNav/')
	nav.connect('togglezoom',self,'toggle')
	
	pos=Vector2(0,0)
	vpos=Vector2(0,0)
	uv=0
	mat=self.get_material()
	panel=self.get_parent()
	
func _process(_delta):
	pos=parent.get_local_mouse_position()
	
	var start = parent.get_position()
	var size = parent.get_size()
		
	uv = pos/size
	uv.x=clamp(uv.x,0,1)
	uv.y=clamp(uv.y,0,1)
	
	mat.set_shader_param("pos",uv)
	
	self.set_position(pos-Vector2(128,128))
