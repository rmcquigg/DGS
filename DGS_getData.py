# -*- coding: utf-8 -*-
"""
Created on Wed May 17 17:24:28 2023

@author: mcquiggan
"""

import pandas as pd
import requests
import xml.etree.ElementTree as ET
import os

def waterLevels (sites):
    dict={}
    with open('readme.txt', 'w') as f:
        f.write('Thanks for downloading water level data from the Delaware Geological Survey!'+
                '\nPlease contact delgeosurvey@udel.edu with any questions.'+
                '\nSiteID = DGS well identifier \nDate = Month/Day/Year \nTime = HHMM Eastern Standard Time'+
                '\nTimeZone = Eastern Standard Time \nWaterLevel = depth to water in feet below ground surface')
    for id in sites:
        url='http://data.dgs.udel.edu/sites/ngwmn/well_waterlevels.php?dgsid='+id
        resp=requests.get(url)
        # a=str(resp.content)
        with open('levels.xml','wb') as foutput:
            foutput.write(resp.content)
        with open('levels.xml') as file:
            tree=ET.parse(file)
            root=tree.getroot()
            df=pd.DataFrame(columns=['SiteID','Date','Time','TimeZone','TimestampISO','WaterLevel']).set_index('TimestampISO')
            for item in root:
                dgsid=item[0].text
                day=item[1].text
                tm=item[2].text
                tz=item[3].text
                tsISO=item[4].text
                wl=item[5].text
                df=df.append(pd.DataFrame({'SiteID':dgsid,'Date':day,'Time':tm,'TimeZone':tz,'TimestampISO':tsISO,
                                             'WaterLevel':wl},index=[tsISO]))
                # d={'df' + str(id):df for id in sites}
                dict[id]=df.set_index('TimestampISO')
                df.to_csv(dgsid+'.csv',index=False)
        os.remove('levels.xml')
    return(dict)        
            
