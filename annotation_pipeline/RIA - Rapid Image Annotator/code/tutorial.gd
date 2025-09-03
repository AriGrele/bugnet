extends Button

var settings
var imgpath
var annpath
var i
var a

signal press(img,ann)

func annupdate():
	annpath=settings.get('settings')['Dirs']['data']
	
func imgupdate():
	imgpath=settings.get('settings')['Dirs']['images']

func _ready():
	settings=get_node('/root/Main/loadsettings/')
	settings.connect('imgchange',self,'imgupdate')
	settings.connect('annchange',self,'annupdate')
	
	imgpath=settings.get('settings')['Dirs']['images']
	annpath=settings.get('settings')['Dirs']['data']
	i=imgpath
	a=annpath
	
func toggle():
	if self.text=='Tutorial':
		self.set_text('Exit tutorial')
		i='res://tutorial/assets/'
		a='res://tutorial/annotations.json'

	else:
		self.set_text('Tutorial')
		i=imgpath
		a=annpath
	emit_signal('press',i,a)

func _on_tutorial_pressed():toggle()
