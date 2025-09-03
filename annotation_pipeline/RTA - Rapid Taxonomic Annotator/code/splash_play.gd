extends AnimationPlayer

func _ready():
	self.play('main')
	
func _on_animation_finished(_anim_name):
	get_node('../../foreground/fadeplayer').play('fade')

func _on_fadeplayer_animation_finished(_anim_name):
	self.get_tree().change_scene_to_file("res://code/main.tscn")
