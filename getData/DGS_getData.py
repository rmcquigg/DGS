# -*- coding: utf-8 -*-
"""
Created on Wed May 17 17:24:28 2023

@author: mcquiggan
"""

import pandas as pd

sites=['Ie55-07','Ie55-06','Ie444-05']

def waterLevels(sites):
    dict={}
    with open('readme.txt', 'w') as f:
        f.write('Thanks for downloading water level data from the Delaware Geological Survey!'+
                '\nPlease contact delgeosurvey@udel.edu with any questions.'+
                '\nSITEID = DGS well identifier \DATE_MEASURED = Month/Day/Year'+
                '\nTIME = HHMM Eastern Standard Time, DM indicates daily average taken from continuous logger-measurements'+
                '\nTIMEZONE= Eastern Standard Time \nWATER_LEVEL = depth to water in feet below ground surface')
    for id in sites:
        url='http://data.dgs.udel.edu/sites/webwatlev/'+id+'.txt'
        try: df=pd.read_csv(url,skiprows=3)
        except:
            print('Data for '+id+' are not available.')
            continue
        df=df.rename(columns=lambda x: x.strip())
        df['SITEID']=id
        df['TIMEZONE']='EST'
        df['newt']=df['TIME'].where(df['TIME']!='DM','0000')
        df['TIMESTAMP']=pd.to_datetime(df['DATE_MEASURED'] + " " + df['newt'])
        df=df.drop('newt',axis=1)
        cols=['SITEID','DATE_MEASURED','TIME','TIMEZONE','WATER_LEVEL','TIMESTAMP']
        df=df[cols]
        dict[id]=df.set_index('TIMESTAMP')
        df.to_csv(id+'.csv',index='TIMESTAMP')
        
    

































