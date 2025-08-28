library(tidyr)
library(yaml)
library(data.table)
library(dplyr)

bar = function(p){                                                              #progress bar
  cat(round(p*100),'% ',paste(c(rep('=',floor(50*p)),rep('-',ceiling(50*(1-p))),'| \r'),collapse=''),sep='')}

plapply = function(X, FUN){                                                     #lapply with progress bar
  lapply(X,\(x){
    bar(match(x,X)/length(X))
    FUN(x)})}

src = '../data/output'                                                          #input folder
data=fread(paste0(src,'/data.txt'))|>
  as.data.frame()|>
  within({
    id=sapply(V1,\(v)strsplit(v,'_')[[1]][1])})                                 #id number for each image

files = data[c('V1','id')]                                                      #image file names
data = setDT(data)                                                              #datatable for faster processing at this point

result=data[, lapply(.SD, mean), by = id, .SDcols = -c(1, ncol(data))]          #average prediction across frames for each insect
data=rename(result,Group.1=id)|>
  as.data.frame()

confidence=data[,-1]                                                            #just the predictions

taxa=read_yaml('../processing_pipeline/model.yaml')$names|>                     #pull out taxon names from model yaml
  suppressWarnings()|>
  unlist()

groups=sapply(taxa,\(t)length(strsplit(t,'_')[[1]]))                            #indeces for knowing which classes are in which taxonomic level

preds=plapply(unique(groups),\(g){                                              #for each taxonomic level
  
  use = taxa[groups==g]
  
  for(taxon in use){                                                            #conditional probabilities if not applied in python script
    bar(match(taxon,use)/length(use))
    col=confidence[,taxa==taxon]
    confidence[grepl(taxon,taxa)&taxa!=taxon&groups==g+1]<<-apply(confidence[grepl(taxon,taxa)&taxa!=taxon&groups==g+1],2,\(x)x*col)}
  
  confidence[,groups==g]<<-t(apply(confidence[,groups==g],1,\(x)x/sum(x)))
    
  data.frame(                                                                   #produce a new data frame with most likely taxon for each group - NB, possible a lower level pred may not match a higher level when e.g. a genus is known but a species is not. be careful to filter these data before using
    'value'=apply(confidence[,groups==g],1,max),
    'id'   =apply(confidence[,groups==g],1,\(x)taxa[groups==g][which(x==max(x))[1]]))})|>
  do.call(cbind,args=_)|>
  setNames(c('order.conf','order','family.conf','family','genus.conf','genus','species.conf','species'))|>
  within({
    id = data[,1]
    family.conf  = order.conf *family.conf
    genus.conf   = family.conf*genus.conf
    species.conf = genus.conf *species.conf})|>
  merge(files,by='id',all=T)

good=list.files(paste0(src,'/images/good/'))|>
  sapply(\(v)strsplit(v,'_')[[1]][1])|>
  as.numeric()

data=subset(preds,id%in%good)                                                   #remove the bad image crops

write.csv(data,'data/formatted_insects.csv',row.names=F)                        #csv of best guesses at all taxonomic levels
