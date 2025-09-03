extends ColorRect

var filename
var units

func load_image(path):
	var image=Image.load_from_file(path)
	var texture=ImageTexture.create_from_image(image)
	return(texture)

func update_texture(file):
	print('file ',file)
	filename=file #make this easily accesable from upper tree
	var mat=self.material
	
	var texture=load_image(file.replace('.import',''))
	if not texture:
		get_node("new_img").hide()
		texture=load_image('res://assets/icon.svg')
		
	if texture:
		get_node("new_img").show()
		var res=texture.get_size()
		mat.set_shader_parameter("tex",texture)
		mat.set_shader_parameter("width", res.x)
		mat.set_shader_parameter("height",res.y)

