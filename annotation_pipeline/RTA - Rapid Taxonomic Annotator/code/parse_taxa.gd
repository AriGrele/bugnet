extends Node2D

var db_name := 'res://data/GBIF_backbone' #path to db file holding GBIF backbone
var db #database variable

var textform #text input scene for taxonomic search

func reset_search():
	textform.create_labels([]) #clear results text

func search(text):
		var results=dbsearch(text) #run sql query
		#print(text)
		textform.create_labels.call_deferred(results) #update results text

func parse_search(text): #for a given string run an sql query and format results
	if text.length()>0: #ignore inputs with <=2 chars as search takes >1 second
		var thread
		thread=Thread.new()
		thread.start(search.bind(text))
		thread.wait_to_finish()
	else:
		textform.create_labels([]) #clear results text if no search performed

func dbsearch(text,n=50): #for given search text and number of results
	db.query('SELECT * FROM taxa WHERE taxon LIKE "'+text+'%" ORDER BY rank DESC, taxon ASC LIMIT '+str(n)) #search names containing string and order by taxonopmic rank, prefering higher rank
	
	var output=[] #holder for results text array
	for i in range(0,min(n,db.query_result.size())): #only return the first n results, or db.size results if fewer than n results
		output.append(db.query_result[i])
		
	return(output)

func _ready():
	textform=get_node('../screen/upper_container/cols/left/options/tabs/Annotate taxa') #taxonomic annotation scene node
	textform.updated.connect(parse_search) #connect to updated signal such that when text entered in form the db search will be run
	textform.applied.connect(reset_search) #to reset search results when names applied to iamges
	
	db = SQLite.new() #create sql database object
	db.path = db_name #load and open GBIF backbone 
	db.verbosity_level = SQLite.VERBOSE
	db.open_db()
	
	
	
	

