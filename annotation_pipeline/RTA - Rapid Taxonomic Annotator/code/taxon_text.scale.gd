extends RichTextLabel

func _process(_delta):
	var height=self.get_size().y
	self.add_theme_font_size_override("normal_font_size", height/2.5)
	self.add_theme_font_size_override("italics_font_size",height/3)
