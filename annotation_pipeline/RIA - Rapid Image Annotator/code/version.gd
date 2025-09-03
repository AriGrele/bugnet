extends Node2D

var version
var req

signal old(new,current)

func _ready():
	req=get_node('HTTPRequest')
	req.connect("request_completed", self, "_on_request_completed")
	req.request("https://arigrele.github.io/Projects/annotator")

func _on_request_completed(_result,_response_code,_headers,body):
	var json=JSON.parse(body.get_string_from_utf8())
	version=json.result['Version']
	
	var settings=get_node('/root/Main/loadsettings/').get('settings')
	var current=settings['Program']['version']
	if version!=current:emit_signal("old",version,current)
