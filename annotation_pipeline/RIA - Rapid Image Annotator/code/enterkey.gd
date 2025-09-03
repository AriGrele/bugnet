extends Panel

var key
var regex

signal save

func _ready():
	hide()
	key=get_node('..')
	
	regex=RegEx.new()
	regex.compile("[A-Z]+_[A-Z]+")

func toggle():
	if self.is_visible():hide()
	else:
		self.set_size(key.get_size())
		show()

func _on_addkey_pressed():toggle()

func _input(ev):
	if self.is_visible():
		var just_pressed = ev.is_pressed() and not ev.is_echo()
		if just_pressed and (ev is InputEventKey):
			
			var text=ev.as_text()
			if text!='Shift':
				print('entered text: ',text)
				toggle()
				var caps=regex.search(text)
				if caps!=null:text=caps.get_string().to_lower()
				
				key.set_text(text)
				key.set('input',ev)
				emit_signal('save')
				

