extends Label

func _ready():
	var data=get_node('/root/Main/loadsettings').get('settings')
	self.set_text(str('Version: ',data['Program']['version'],'\nLast updated: ',data['Program']['updated']))
