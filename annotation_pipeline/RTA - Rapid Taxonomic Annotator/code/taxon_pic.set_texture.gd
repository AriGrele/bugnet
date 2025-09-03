extends ColorRect

var filename
var fullname=''
var units

func update_text(endtext,full):
	fullname=full
	get_node('../taxon_text').set_text(str(units,endtext))
	
func load_image(path):
	var image=Image.load_from_file(path)
	var texture=ImageTexture.create_from_image(image)
	return(texture)

func update_texture(file):
	filename=file #make this easily accesable from upper tree
	var mat=self.material
	
	var texture=load_image(file)
	if texture:
		var res=texture.get_size()
		mat.set_shader_parameter("tex",texture)
		mat.set_shader_parameter("width", res.x)
		mat.set_shader_parameter("height",res.y)
		mat.set_shader_parameter("confirmed",false)
		
		var conversion=1.0/100.0
		var ratio=clamp(res.x/res.y,0,1)
		var cm=1.0/(conversion*res.x/ratio)*100.0
		
		units='[i]1 cm[/i]\n'
		
		if cm>100.0:
			cm/=10
			units='[i]1 mm[/i]\n'
			
		update_text('\nDefault endtext','Default')
		get_node('../scale_slider').set_value(cm)

func confirm(check):
	var mat=self.material
	mat.set_shader_parameter("confirmed",check)

