extends Label

var items
var nav
var starttime

func sum(x):
	var out=0
	for i in x:out+=i
	return(out)
	
func ave(x):return(sum(x)/len(x))

func disp_time(t):
	t = float(t)*100 #dumb way to round 2 decimal places
	if t>3600*24*100:return(str(round(t/3600/24)/100,' days'))
	if t>3600*100:   return(str(round(t/3600)/100,' hours'))
	if t>60*100:     return(str(round(t/60)/100,' minutes'))
	
	return(str(round(t)/100,' seconds'))

func median(x):
	x.sort()
	return(x[floor((len(x)+1.0)/2.0)-1.0])

func pagechange(dic):
	dic['prev']=dic['Index']
	dic['Index']=nav.get('index')
	dic['Images']=len(nav.get('data'))
	dic['Images']=str(dic['Images']-dic['Index'],' out of ',dic['Images'])
	if 'times' in dic.keys():
		if len(dic['times'])>0:
			dic['Average time']=ave(dic['times'])
			dic['Average time']=str(disp_time(dic['Average time']),'\nRemaining: ',disp_time(ave(dic['times'])*(len(nav.get('data'))-dic['Index'])))
		else:
			dic['Average time']=''
			
	return(dic)

func load_items(dic):
	if dic['Index']!=dic['prev']:
		dic['Images']=len(nav.get('data'))
		dic['Images']=str(dic['Images']-dic['Index'],' out of ',dic['Images'])
		if not 'Pages' in dic.keys():dic['Pages']=0
		dic['Pages']+=1
		dic['Start time']=starttime
		
		if 'times' in dic.keys():
			dic['times'].append(OS.get_system_time_msecs()/1000.0-dic['Time'])
		else:dic['times']=[]
		
		dic['Time']=OS.get_system_time_msecs()/1000.0
		
		dic['Current time']=disp_time(dic['Time']-dic['Start time'])
		if len(dic['times'])>0:
			dic['Average time']=ave(dic['times'])
			dic['Average time']=str(disp_time(dic['Average time']),'\nRemaining: ',disp_time(ave(dic['times'])*(len(nav.get('data'))-dic['Index'])))
			dic['Median time']=median(dic['times'])
		else:
			dic['Average time']=''
			dic['Median time']=''
	
	update()
	return(dic)

func _ready():
	nav=get_node('/root/Main/ImageNav')
	nav.connect('savebox',self,'refresh')
	nav.connect('pagechange',self,'page')
	
	starttime=OS.get_system_time_msecs()/1000.0
	
	items=load_items({'Index':nav.get('index'),'prev':nav.get('index')})
	refresh()
	
func format(dic):
	var output=''
	for k in ['Index','Images','Current time','Average time']:
		if k in items.keys():output+=str(k,': ',dic[k],'\n')

	return(output)
	
func page():
	items=pagechange(items)
	self.set_text(format(items))
	
func refresh():
	items=load_items(items)
	self.set_text(format(items))
