extends Node2D

func load_file(file): #loads a JSON file as dict variable
	var f = FileAccess.open(file, FileAccess.READ)
	if f == null:
		print(str("Error: File not found or couldn't be opened: ", file))
		return null
		
	var text='' #to hold output
	while not f.eof_reached(): #until the end of the file, add new lines to text
		text+=f.get_line()
	f.close()
	
	var json_object = JSON.new()
	var error=json_object.parse(text) #returns a JSON formatted object from text input
	
	if !error:return(json_object.data) #return this object if no errors in parsing
	else:print(str("Error loading JSON file at path: ",file,"\nError: ",error)) #print error if called

func save_file(file,data):
	var json_string = JSON.stringify(data,'\t')
	
	var output = FileAccess.open(file,FileAccess.WRITE)
	output.store_string(json_string)

func dir_contents(path):
	var files=[]
	var dir=DirAccess.open(path)
	if dir:
		dir.list_dir_begin()
		var file=dir.get_next()
		
		while file!="":
			if dir.current_is_dir():pass
			else:
				files.append(str(path,'/',file))
			file=dir.get_next()
		return(files)
		
	else:
		print("An error occurred when loading ",path)
		return(null)
