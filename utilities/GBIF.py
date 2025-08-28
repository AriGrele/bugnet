from pygbif import occurrences as occ
from pygbif import species

from utilities.functions import progress
from collections import Counter

import pandas as pd
import zipfile
import os
import time

class GBIF():                                                                   #main class for interacting with GBIF data
    def __init__(self,latlong=None):
        self.data={}
        self.keys=[]

        self.latlong = latlong                                                  #center point of search area

    def get(self,src=None,columns=[]):                                          #get data from cols
        self.data=self.get_data(src,usecols=columns)

    def merge(self,src=None,columns=[],by=''):                                  #merge in new dataframe to current data
        data=self.get_data(src,usecols=columns)
        self.data=self.data.merge(data,left_on=by,right_on=by)

    def concat(self,src=None,columns=[]):                                       #concat columns into single col
        data=self.get_data(src,usecols=columns)
        self.data=pd.concat([self.data,data],ignore_index=True)
        
    def unique(self,col):                                                       #unique values in a col
        return(list(set(self.data[col])))

    def count(self,col):                                                        #class count from col
        return(Counter(self.data[col]))

    def filter(self,col,items,op='in'):                                         #methods of filtering data - inclusive, exclusive, inequality 
        if op=='in':
            self.data=self.data[self.data[col].str.lower().isin(items)]
        if op=='out':
            self.data=self.data[~(self.data[col].str.lower().isin(items))]
        if op=='<=':
            self.data=self.data[self.data[col]<=items]

    def write(self,dst):                                                        #save data frame to csv
        self.data.to_csv(dst,index=False)
        
    def region(self,keys,size):                                                 #grab occurence data from coords
        print(f'\nGenerating list of taxa within {size}° of {self.latlong}')

        self.download(keys,
         ['occurrenceStatus = present',
          f'decimalLatitude <= {self.latlong[0]+size}',
          f'decimalLongitude <= {self.latlong[1]+size}',
          f'decimalLatitude >= {self.latlong[0]-size}',
          f'decimalLongitude >= {self.latlong[1]-size}'])

    def download(self,keys,args=[],output='SIMPLE_CSV',pred_type='and'):        #download occurence data from taxon keys and further args
        for file in os.listdir('../data/database_pipeline/gbif_downloads'):
            os.remove(f'../data/database_pipeline/gbif_downloads/{file}')       #remove last search result to avoid filling up disk space
        
        if type(keys) is dict:
            results=occ.download(keys,format=output)
        else:
            results=occ.download(keys+args,format=output,pred_type=pred_type)

        while occ.download_meta(key=results[0])['status'] in ['PREPARING','RUNNING']: #check every .5 seconds if download finished
            for i in ['|','/','—','\\','|','/','—','\\','|','/','—','\\','|']: #loading wheel
                print('Downloading GBIF occurrence data . . . ',i,end='\r')
                time.sleep(.5)
            
        occ.download_get(results[0],path='../data/database_pipeline/gbif_downloads')  #get the actual data from GBIF

    def get_data(self,filename=None,usecols=None):                              #extract zip and grab data
        while True:                                                             #I cannot remember why I did this. I think the way this interacts with the rest of the scripts this will not enter an infinite loop - it will either return or break with an error
            download=os.listdir('../data/database_pipeline/gbif_downloads')[-1]
            with zipfile.ZipFile(f'../data/database_pipeline/gbif_downloads/{download}') as extract:

                if filename:
                    for item in extract.infolist():
                        if item.filename.split('/')[-1]==filename:
                            data=pd.read_csv(extract.open(item),sep='\t',usecols=usecols, low_memory = False)
                            return(data)
                else:
                    data=pd.read_csv(extract.open(extract.infolist()[0]),sep='\t',usecols=usecols, low_memory = False)
                    return(data)
            
    def metadata(self,columns):                                                 #grab data asscoiated with obs, especially taxonomic data
        for col in columns:
            print(f'\nAccessing metadata for {len(self.unique(col))} taxa')
            for i,taxon in enumerate(self.unique(col)):
                progress('',(i+1)/len(self.unique(col)))

                for retry in range(5):
                    try:
                        backbone=species.name_usage(name=taxon)['results']
                        self.keys+=[row[f'{col}Key'] for row in backbone if f'{col}Key' in row]
                        break
                    except Exception:
                        time.sleep(.1) 
