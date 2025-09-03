extends Panel

var check

func display(version,current):
	var text=str('You are currently using version ',current,'\nThe most recent version is ',version,'\nConsider updating:')
	get_node("Label").set_text(text)
	self.show()
	
func _ready():
	self.hide()
	check=get_node('/root/Main/version/')
	check.connect('old',self,'display')

func _on_link_pressed():
	var _shell = OS.shell_open(get_node("link").text)
	self.hide()

func _on_close_pressed():self.hide()
