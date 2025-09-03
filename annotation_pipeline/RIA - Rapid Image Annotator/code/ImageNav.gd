extends Node2D

var base='res://assets/default image.png'
var imagename='No image loaded'
var img_folder=''
var loadstate=0

var texture
var sprite
var text
var index
var data

var settingpanel
var dialog

var regex
var keyname

signal pagechange
signal savebox
signal clearbox
signal cyclebox(dir)
signal delbox
signal margin(side,dir)
signal togglezoom
signal comment(comment,key)

var error

var controls 
var parsecontrols

var settings
var ticker

var mousereg

var zoom

var tutorial
var loaded=false

func _ready():pass


func final_ready():
	loaded=true
	mousereg=RegEx.new()
	mousereg.compile("[A-Z]+_[A-Z]+")
	
	settings=get_node('/root/Main/loadsettings/').get('settings')
	
	var path=settings['Dirs']['images']
	index=0
	error=true
	
	data=dir_contents(path)
	
	text         = get_node("../View/CanvasLayer/hbox/vbox/CenterPanel/missinglabel")
	sprite       = get_node("../View/CanvasLayer/hbox/vbox/CenterPanel")
	zoom         = get_node("../View/CanvasLayer/hbox/vbox/CenterPanel/zoom_shader/Viewport/image")
	settingpanel = get_node('../View/CanvasLayer/Center/Settings')
	dialog       = get_node('../View/CanvasLayer/Center/ImageLoad')
	ticker       = get_node('../View/CanvasLayer/TopRight/TextEdit')
	
	base_image()
	text.show()
	
	regex=RegEx.new()
	regex.compile("^.+\\/")
	
	keyname=RegEx.new()
	keyname.compile("[A-Z]+_[A-Z]+")
	
	change_image(settings['Images']['index'])
	
func base_image():
	var material=sprite.get_material()
	var zoommat=zoom.get_material()
	material.set_shader_param("tex",load(base))
	zoommat.set_shader_param("tex",load(base))
	text.show()

func update_image(path):
	var material=sprite.get_material()
	var zoommat=zoom.get_material()
	var tex=load_image(path)
	if tex==null:
		material.set_shader_param("tex",load(base))
		zoommat.set_shader_param("tex",load(base))
		text.show()
		error=true
	else:
		material.set_shader_param("tex",tex)
		zoommat.set_shader_param("tex",tex)
		text.hide()
		error=false

func change_image(dir=1):
	if data!=null and len(data)>0:
		index+=dir
		index=clamp(index,0,len(data)-1)
		ticker.set_text(str(index))
		update_image(data[index])
		imagename=regex.sub(data[index],'')
		emit_signal('pagechange')

func dir_contents(path):
	var files=[]
	var dir=Directory.new()
	if dir.open(path)==OK:
		dir.open(path)
		dir.list_dir_begin()

		while true:
			var file=dir.get_next()
			if file=="":break
			elif dir.current_is_dir():pass
			elif not (file.begins_with(".") or '.import' in file):files.append(path+'/'+file)

		dir.list_dir_end()

	else:print(str('Error loading folder',path))
	return(files)

func load_image(path):
	var image=Image.new()
	var err=image.load(path)
	if err==OK:
		texture=ImageTexture.new()
		texture.create_from_image(image,0)
	else:
		print(str('Error loading image: ',path))
		return(null)
	return(texture)

func _on_ImageLoad_dir_selected(dir):
	index=0
	data=dir_contents(dir)
	change_image(0)

func toggle_tutorial(img):
	index=0
	data=dir_contents(img)
	change_image(-100000000)

func _on_pageleft_pressed():
	change_image(-1)

func _on_pageright_pressed():
	change_image()

func revdict(d):
	var out={}
	for k in d.keys():
		for item in d[k]:
			item=item.as_text()
			var mousecheck=mousereg.search(item)
			if mousecheck!=null:item=mousecheck.get_string().to_lower()
					
			if not item in out.keys():out[item]=[]
			out[item].append(k)
	return(out)

func _process(_delta):
	if !loaded:
		print('loading')
		final_ready()
	
	if Input.is_action_pressed('bmu'):  emit_signal('margin',2, 1)
	elif Input.is_action_pressed('tmu'):emit_signal('margin',0, 1)
	
	if Input.is_action_pressed('bmd'):  emit_signal('margin',2,-1)
	elif Input.is_action_pressed('tmd'):emit_signal('margin',0,-1)
	
	if Input.is_action_pressed('lmr'):  emit_signal('margin',3, -1)
	elif Input.is_action_pressed('rmr'):emit_signal('margin',1, 1)
	
	if Input.is_action_pressed('lml'):  emit_signal('margin',3,1)
	elif Input.is_action_pressed('rml'):emit_signal('margin',1,-1)

func _input(ev):
	if loaded:
		if not settingpanel.is_visible() and not dialog.is_visible():
			var just_pressed = ev.is_pressed() and not ev.is_echo()
			var mouse=get_local_mouse_position()
			
			if just_pressed and (ev is InputEventMouseButton or ev is InputEventKey) and mouse.y>27:
				
				var textout=ev.as_text()
				
				var caps=keyname.search(textout)
				
				if caps!=null:
					textout=caps.get_string().to_lower()
				controls=settings['Controls']['controls']
				var com={}
				for k in settings['Comments']['comments']['Comments'].keys():
					com[k.as_text()]=settings['Comments']['comments']['Comments'][k]
				controls=revdict(controls)
				if textout in controls.keys():
					controls[textout].invert()
					for cmd in controls[textout]:
						match cmd:
							'Prev image':        change_image(-1)
							'Next image':        change_image()
							'Save data':         emit_signal('savebox')
							'Clear data':        emit_signal('clearbox')
							'Prev box':          emit_signal('cyclebox',-1)
							'Next box':          emit_signal('cyclebox', 1)
							'Delete box':        emit_signal('delbox')
							'Zoom':              emit_signal('togglezoom')
							'Comments':          emit_signal('comment',com[ev.as_text()],ev.as_text())
							'Top margin up':     pass
							'Top margin down':   pass
							'Right margin right':pass
							'Right margin left': pass
							'Left margin right': pass
							'Left margin left':  pass
							'Bottom margin up':  pass
							'Bottom margin down':pass
							_:print('cmd: ',cmd,ev.as_text())

func _on_TextEdit_text_entered(new_text):
	change_image(int(new_text)-index)
