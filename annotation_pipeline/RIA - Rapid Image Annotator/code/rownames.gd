extends Label
	
func _ready():
	var settings=get_node('/root/Main/loadsettings').get('settings')
	var text=''
	for item in settings['Names']['names']:text+=item+'\n'
	self.set_text(text)
