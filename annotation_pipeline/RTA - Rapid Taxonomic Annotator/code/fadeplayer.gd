extends AnimationPlayer

func _ready():
	self.play('fadein')

func _on_animation_finished(anim_name):
	self.get_parent().hide()
