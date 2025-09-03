extends TextureRect


func _ready():
	#var thread
	#thread=Thread.new()
	#thread.start(rotate)
	#thread.wait_to_finish()
	pass
	
func rotate():
	var rot=0
	while true:
		rot+=.1
		await get_tree().create_timer(1./60.).timeout
		self.set_rotation.call_deferred(rot)
		queue_redraw()
