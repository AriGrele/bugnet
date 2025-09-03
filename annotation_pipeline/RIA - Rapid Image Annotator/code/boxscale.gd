extends HBoxContainer

func _ready():pass

func _process(_delta):
	var window_size=get_viewport_rect().size
	self.set_size(window_size-Vector2(256,27))
