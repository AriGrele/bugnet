extends Label

var nav

func changetext():
	var image=nav.get('imagename').replace('.jpg','').replace('-',' ').replace('_','\n          ')
	self.set_text('Filename:\n          '+image)

func _ready():
	nav=get_node('/root/Main/ImageNav')
	nav.connect('pagechange',self,'changetext')
	changetext()

func _on_ImageLoad_dir_selected(_dir):
	changetext()

func _on_pageleft_pressed():
	changetext()

func _on_pageright_pressed():
	changetext()
