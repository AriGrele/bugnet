extends Node2D

var boxes
var imgcom
var start=null
var end
var running=false
var count
var mouse    = Vector2(0,0)
var previous = Vector2(0,0)
var pos      = Vector2(0,0)
var corner   = Vector2(256,27)
var size     = Vector2(485,485)
var path
var nav
var menu
var dialog
var colors
var pos1
var pos2
var alldata
var imgname
var sel
var tutorial
var comcolor
var commentbox
var settings
var font
var shapes
var shapetype= 'box'
var deselect = false

func absv2(v2):return(Vector2(abs(v2.x),abs(v2.y)))

func box(ar): #[v2,v2,u] -> [x,y,w,h]
	var center=(ar['start']+ar['end'])/2
	var dim=absv2(ar['end']-ar['start'])
	if len(ar.keys())>0:
		var out={'box':[center.x,center.y,dim.x,dim.y]}
		for k in ar.keys():
			if not k in ['start','end']:out[k]=ar[k]
		return(out)
	return([center.x,center.y,dim.x,dim.y])

func unbox(ar): #[x,y,w,h,u] -> [v2,v2,u]
	if typeof(ar)==TYPE_ARRAY:
		var center=Vector2(ar[0],ar[1])
		var dim=Vector2(ar[2],ar[3])
		return({'start':Vector2(center-dim/2),'end':Vector2(center+dim/2)})
	var points=ar['box']
	var center=Vector2(points[0],points[1])
	var dim=Vector2(points[2],points[3])
	
	var out={'start':Vector2(center-dim/2),'end':Vector2(center+dim/2)}
	for k in ar.keys():
		if k!='box':out[k]=ar[k]
	return(out)
	
func load_file(file):
	var f=File.new()
	f.open(file,File.READ)
	var text=''
	while not f.eof_reached():
		text+=f.get_line()
	f.close()
	var data=JSON.parse(text).result
	var output={}
	if data!=null:
		for k in data.keys():
			output[k]={}
			for item in data[k].keys():
				if str(item).split('_')[0]=='Comment':
					output[k][item]=data[k][item]
				else:
					output[k][int(item)]=unbox(data[k][item])
		return(output)
	else:return(load_file('res://data/annotations.json'))
	
func save_file(file,data):
	var output={}
	for k in data.keys():
		output[k]={}
		for item in data[k].keys():
			if str(item).split('_')[0]=='Comment':
				output[k][item]=data[k][item]
			else:
				output[k][item]=box(data[k][item])
	var text=JSON.print(output,'\t')
	
	var f=File.new()
	f.open(file,File.WRITE)
	if (f.is_open()):
		f.store_string(text)
		f.close()

func v2clamp(v2,lower,upper):
	return(Vector2(clamp(v2.x,lower,upper),clamp(v2.y,lower,upper)))

func savebox():
	imgname=nav.get('imagename')
	alldata[imgname]=boxes.duplicate(true)
	for key in imgcom.keys():alldata[imgname][key]=imgcom[key]
	save_file(path,alldata)
		
func clearbox():
	boxes={}
	count=0
	sel=-1

func cyclebox(dir):
	if sel>-1:
		sel+=dir
		var n=len(boxes.keys())
		if sel<0:sel=n-1
		if sel>=n:sel=0
	
	else:sel=0

func delbox():
	if len(boxes.keys())>0 and sel>-1:
		boxes.erase(boxes.keys()[sel])
		sel=-1

func margin(side,dir):
	if len(boxes.keys())>0 and sel>-1:
		var select=boxes.keys()[sel]
		var c1
		var c2
		
		var s=boxes[select]['start']
		var e=boxes[select]['end']
		var trans=[Vector2(0,-1),Vector2(1,0),Vector2(0,-1),Vector2(-1,0)][side]
		if side==0 or side==1:
			c1=Vector2(max(s.x,e.x),min(s.y,e.y))
			c2=Vector2(min(s.x,e.x),max(s.y,e.y))
		if side==2 or side==3:
			c1=Vector2(min(s.x,e.x),max(s.y,e.y))
			c2=Vector2(max(s.x,e.x),min(s.y,e.y))
		boxes[select]['end']=c2
		boxes[select]['start']=c1+trans*dir/500
		boxes[select]['user']='human'
	
func init():
	imgname=nav.get('imagename')
	if imgname in alldata.keys():
		boxes=alldata[imgname].duplicate(true)
	else:boxes={}
	
	imgcom={}
	
	for key in boxes.keys():
		if str(key).split('_')[0]=='Comment':
			imgcom[key]=boxes[key]
			boxes.erase(key)
	
	count=boxes.keys().max()
	if count == null: count = 0
	sel=-1
	
	dispcom()

func gen_colors():
	comcolor={}
	var coms=settings['Comments']['comments']['Comments']
	seed(0)
	for k in coms.keys():
		var r=randf()/2.0+0.25
		var g=randf()/2.0+0.25
		var b=randf()/2.0+0.25
		comcolor[k.as_text()]=Color(r,g,b,.5)

func dispcom():
	var text='Comments:\n'
	for key in imgcom.keys():
		text+=str('     ',key.replace('Comment_',''),', ')
	commentbox.set_text(text)

func set_comment(comment,key):
	if len(boxes.keys())>0 and sel>-1:
		var com=str('Comment_',key)
		if com in boxes[boxes.keys()[sel]].keys():boxes[boxes.keys()[sel]].erase(com)
		else:
			boxes[boxes.keys()[sel]][com]=comment
			
	else:
		var com=str('Comment_',key)
		if com in imgcom.keys():imgcom.erase(com)
		else:
			imgcom[com]=comment
			
		dispcom()

func change_shape(type):
	shapetype=type

func _ready():
	font=DynamicFont.new()
	font.font_data=load("res://assets/AlegreyaSans-Regular.ttf")
	font.size=15

	alldata={}
	boxes={}
	imgcom={}

	settings   = get_node('/root/Main/loadsettings').get('settings')
	menu       = get_node('/root/Main/View/CanvasLayer/Center/ImageLoad')
	dialog     = get_node('/root/Main/View/CanvasLayer/Center/Settings')
	colors     = get_node('/root/Main/View/CanvasLayer/Center/Settings/margin/ColorPanel/testdraw')
	commentbox = get_node('/root/Main/View/CanvasLayer/PageCenter/LeftPanel/box/comments')
	nav        = get_node('/root/Main/ImageNav/')
	shapes     = get_node('/root/Main/View/CanvasLayer/Center/Settings/shape')
	path       = settings['Dirs']['data']
	
	alldata=load_file(path)
	
	shapes.connect('shape',  self,'change_shape')
	nav.connect('pagechange',self,'init')
	nav.connect('savebox',   self,'savebox')
	nav.connect('clearbox',  self,'clearbox')
	nav.connect('cyclebox',  self,'cyclebox')
	nav.connect('delbox',    self,'delbox')
	nav.connect('margin',    self,'margin')
	nav.connect('comment',   self,'set_comment')
	imgname=nav.get('imagename')
	
	init()

func _process(_delta):
	previous=mouse
	pos=(get_local_mouse_position()-corner)/size
	mouse=v2clamp(pos,0,1)
	
	if not nav.get('error') and not menu.is_visible() and not dialog.is_visible():
		if Input.is_action_just_pressed("mouse_left"):
			running=true
			pos1=mouse
			
		if running:
			if mouse!=pos1:pos2=mouse
		
		if Input.is_action_just_released("mouse_left") and running:
			deselect = true
			
			if mouse!=pos1 and pos1!=null:
				count+=1
				var dim=(pos2*size+corner-(pos1*size+corner))
				if abs(dim.x)+abs(dim.y)>0:
					boxes[count]={'start':pos1,'end':pos2,'user':'human'}
			
			running=false
			pos1=null
			pos2=null
	else:
		pos1=null
		pos2=null

	update()

func dboxi(Start,dim,fill):draw_rect(Rect2(Start,dim),fill,true)

func dcirclei(Start,dim,fill):draw_circle(Vector2(Start),sqrt(dim.x*dim.x+dim.y*dim.y),fill)

func draw_inner(Start,dim,fill,type):
	match type:
		'box'   :dboxi(Start,dim,fill)
		'line'  :pass
		'circle':dcirclei(Start,dim,fill)
		
func dbox(Start,dim,fill,cols,type):
	draw_inner(Start,dim,fill,type)
	draw_rect(Rect2(Start-Vector2(1,1),dim+Vector2(2,2)),cols['outer'],false,3)
	draw_rect(Rect2(Start,dim),cols['inner'],false,1)

func dline(Start,dim,cols):
	draw_line(Vector2(Start),Vector2(Start+dim),cols['inner'],1,true)

func dcircle(Start,dim,fill,_cols):
	draw_circle(Vector2(Start),sqrt(dim.x*dim.x+dim.y*dim.y),fill)
	
func draw_all(Start,dim,fill,cols,type):
	match type:
		'box'   :dbox(Start,dim,fill,cols,type)
		'line'  :dline(Start,dim,cols)
		'circle':dcircle(Start,dim,fill,cols)
	
func _draw():
	var color=colors.get('cols')
	
	if pos==mouse and not nav.get('error') and not menu.is_visible() and not dialog.is_visible():
		var coords=pos*size+corner
		draw_line(Vector2(coords.x,size.y+corner.y),Vector2(coords.x,corner.y),color['lines'])
		draw_line(Vector2(size.x+corner.x,coords.y),Vector2(corner.x,coords.y),color['lines'])
	
	var boxcheck=0
	for key in boxes.keys():
		start=boxes[key]['start']
		end=boxes[key]['end']
		if (clamp(pos.x,end.x,start.x)==pos.x or clamp(pos.x,start.x,end.x)==pos.x) and (clamp(pos.y,end.y,start.y)==pos.y or clamp(pos.y,start.y,end.y)==pos.y):
			sel=boxes.keys().find(key)
			boxcheck+=1
			deselect = false
			
	if boxcheck==0 and previous!=mouse:
		if dialog.get('select'):sel=-1 #only deselect boxes when mouse is outside all and moving when deselect toggled in settings
	
	if deselect: sel = -1
		
	for key in boxes.keys():
		var cols={'outer':color['outer'],'inner':color['inner'],'fill':Color(0,1,1,.25),'lines':color['lines']}
		if 'user' in boxes[key].keys():cols=color
		var fill=cols['fill']
		
		start = boxes[key]['start']*size+corner
		end   = boxes[key]['end']*size+corner
		var dim=Vector2((end.x-start.x),(end.y-start.y)) ##see below re abs and min
		
		var center = corner + Vector2(250,250)
		var corners = [start, Vector2(end.x,start.y), end, Vector2(start.x,end.y)]
		
		var pd = [0,1,2,3]
		for i in pd: pd[i] = (corners[i]-center).length_squared()
		
		var close = pd.find(pd.min())
		
		if abs(dim.x)+abs(dim.y)>0:
			if key==boxes.keys()[sel] and sel>-1:
				draw_inner(start,dim,fill,shapetype)
			draw_all(start,dim,fill,cols,shapetype)
		
			var comcount=-1
			for k in boxes[key]:
				if str(k).split('_')[0]=='Comment':
					comcount+=1
					
					var textdir = -Vector2(0,5+comcount*12)
					if close>1: textdir = Vector2(0,10+comcount*12)
					
					if close == 1 or close == 2:
						draw_string(font,corners[close]+textdir,boxes[key][k],Color(0,0,0))
					else:
						draw_string(font,corners[close]+textdir-Vector2(font.get_string_size(boxes[key][k]).x, 0),boxes[key][k],Color(0,0,0))
		
	if pos1!=null and pos2!=null:
		var pos1m=pos1*size+corner
		var pos2m=pos2*size+corner
		var dim=Vector2((pos2m.x-pos1m.x),(pos2m.y-pos1m.y)) #removed the code for abs and min pos1 and dim, may break something in the future?

		draw_all(pos1*size+corner,dim,color['fill'],color,shapetype)

func _on_DataLoad_file_selected(dir):
	save_file(path,alldata)
	path=dir
	_ready()
	
func toggle_tutorial(ann):
	save_file(path,alldata)
	path=ann
	_ready()
	
func _on_cycleup_pressed():
	cyclebox(1)

func _on_cycledown_pressed():
	cyclebox(-1)
