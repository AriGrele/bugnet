extends Node2D

var version
var req

signal old(new,current)

func _ready():
	req=get_node('HTTPRequest')
	req.request_completed.connect(_on_request_completed)
	req.request("https://arigrele.github.io/Projects/RTA_version")

func _on_request_completed(_result,_response_code,_headers,body):
	var json= JSON.new()
	var error = json.parse(body.get_string_from_utf8())
	version = json.data['Version']
	
	var settings=get_node('../settings/').get('settings')
	var current=settings['misc']['version']
	if version!=current:emit_signal("old",version,current)
