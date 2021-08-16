# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 15:53:47 2021

@author: mcquiggan
"""

#Insert WQ lab data
import numpy as np
import datetime as dt
import pandas as pd
import os
import warnings

def tests(path,agency,test_source,user_name):
    warnings.filterwarnings('ignore')    
    df=pd.read_csv(path)
    file=path.split(sep='/')[-1]
    #This is specifically for DNREC ELS lab EDDs
    df=df.drop(['CustomerName','ProjectName','OrderID','ELSSampleNumber','Site','Matrix',
                'Analysis Time','LOQ','FieldQC','Dilution','Qualifier'],axis=1,errors='ignore')
    df=df.rename(columns={'ReportingUnits':'units','Parameter':'test','Collect Date':'date_sampled',
                          'Collect Time':'time','Analysis Date':'date_analyzed','Method':'test_method'})
    #Change parameter names to Watsys test codes
    from functools import reduce
    dc={'Potassium, Dissolved':'K','Iron, Dissolved':'FED','Chloride, Dissolved':'CL','Silica, Dissolved':'SI',
        'Nitrate as N, Dissolved':'N3','Nitrite as N, Dissolved':'N2','Magnesium, Dissolved':'MG',
        'Bromide, Dissolved':'BR','Alkalinity (Titrimetric, pH 4.5), Dissolved':'ALK','Sulfate, Dissolved':'SO4',
        'Sodium, Dissolved':'NA','Nitrate/Nitrite as N, Dissolved':'NT','Residue, Filterable (TDS)':'TDS',
        'Calcium, Dissolved':'CA','Chromium, Dissolved':'CR','Mercury, Dissolved':'HG','Manganese, Dissolved':'MN',
        'Copper, Dissolved':'CU','Iron, Dissolved':'FED','Arsenic, Dissolved':'AS','Lead, Dissolved':'PB','Zinc, Dissolved':'ZN',
        'Cadmium, Dissolved':'CD'}
    df['test']=reduce(lambda x, y: x.replace(y,dc[y]),dc,df['test'])
    #Another way to run through the dict
    # par=df['test']
    # test=[]
    # for p in par:
    #     test.append(dc.get(p,p))
    
    #Change test methods to Watsys codes
    methdc={'APHA 2320':'SM2320',
            'EPA 200.8':'EPA200.8',
            'EPA 200.7':'EPA200.7',
            'APHA 4500-CL-(E)':'SM4500CL',
            'EPA 300.0':'EPA300.0',
            'EPA 245.1 CLP-M':'EPA245.1',
            'USEPA 353.2':'EPA353.2',
            'APHA 2540-C':'SM2540C',
            'APHA 2450':'SM2450',
            'EPA 170.1':'EPA170.1',
            'EPA 120.1':'EPA120.1',
            'EPA 150.1':'EPA150.1',
            'NAM':'SM4500',
            'COD':'EPA410.4',
            'APHA 4500-SIO2-C':'SM4500SIO2C',
            'EPA 360.1':'EPA360.1'}
    df['test_method']=reduce(lambda x, y: x.replace(y,methdc[y]),methdc,df['test_method'])
    
    df['dgsid']=(df['CustomerSampleNumber']).astype(str)
    df['amount']=np.where(df['Result']=='ND',df['MDL'],df['Result'])
    choices=['CL','NA','K','TDS','SO4','CA','ALK','SI','N2','NT','N3','MG']
    mask=df['test'].isin(choices)
    dfsub=df[mask]
    dfsub['amount']=np.where(dfsub['units']=='ug/L',((dfsub['amount']).astype(float)/1000).map(lambda x: '{:.6f}'.format(x).rstrip('0')),dfsub['amount'].astype(float))
    df=df[~mask]
    #df['amount']=np.where(df['units']=='ug/L',((df['amount']).astype(float)/1000).map(lambda x: '{:.6f}'.format(x).rstrip('0')),df['amount'].astype(float))
    dfsub['units']='M'
    dfsub['units']=np.where(dfsub['Result']=='ND','L'+dfsub['units'],dfsub['units'])
    df['units']=np.where(df['units']=='ug/L','U',df['units'])
    df['units']=np.where(df['units']=='mg/L','M',df['units'])
    df['units']=np.where(df['Result']=='ND','L'+df['units'],df['units'])
    df=df.append(dfsub).sort_values(by='CustomerSampleNumber')
    
    df['date_sampled']=pd.to_datetime(df['date_sampled']).dt.strftime('%m/%d/%Y')
    df['date_analyzed']=pd.to_datetime(df['date_analyzed']).dt.strftime('%y%m%d')
    #Only run next statement if there any blanks in date_analyzed
    #df['date_analyzed'] = df['date_analyzed'].replace('NaT','')
    df['time']=pd.to_datetime(df['time']).dt.strftime('%H%M')
    df=df.assign(sampleid=lambda df:df['date_sampled']+df['dgsid']+'G',
              testid= lambda df:df['date_sampled']+df['dgsid']+df['test'])
    df=df.drop(['CustomerSampleNumber','MDL','Result'],axis=1)
    
    system_date=dt.date.today().strftime('%d-%b-%Y')
    
    #Remove duplicate flags from DGSIDs
    df['dgsid']=np.where(df.dgsid.str[-1:]=='D',df.dgsid.str[:-1],df.dgsid)
    
    df['SQL']=("""insert into tests (system_date,user_name,test_source,agency,dgsid,date_sampled,\
    sampleid,date_analyzed,test,testid,test_method,units,amount) values ('""")+system_date+"','"+\
        user_name+"','"+test_source+"','"+agency+"','"+df['dgsid']+"','"+\
        df['date_sampled']+"','"+df['sampleid']+"','"+df['date_analyzed']+"','"+\
        df['test']+"','"+df['testid']+"','"+df['test_method']+"','"+df['units']+"',"+\
        df['amount'].astype(str)+");"
    endpath=os.path.split(path)[0]    
    df.to_csv(endpath+'/tests_upload_'+file,index=False,columns=['SQL'])

def quality(path,agency,user_name,record_by,sam_method):
    
    df=pd.read_csv(path)
    file=path.split(sep='/')[-1]
    #This is specifically for DNREC ELS lab EDDs
    df=df.drop(['CustomerName','ProjectName','OrderID','ELSSampleNumber','Site','Matrix',
                'Analysis Time','LOQ','FieldQC','Dilution','Qualifier','Result','ReportingUnits',
                'Parameter','Analysis Date','MDL'],axis=1,errors='ignore')
    df=df.rename(columns={'Collect Date':'date_sampled',
                          'Collect Time':'time','Method':'test_method'})
        
    df['dgsid']=(df['CustomerSampleNumber']).astype(str)
    df['date_sampled']=pd.to_datetime(df['date_sampled']).dt.strftime('%m/%d/%Y')
    df['time']=pd.to_datetime(df['time']).dt.strftime('%H%M')
    df=df.assign(sampleid=lambda df:df['date_sampled']+df['dgsid']+'G')
    df=df.drop(['CustomerSampleNumber'],axis=1)
    
    df['system_date']=dt.date.today().strftime('%d-%b-%Y')
   
    df=df[['date_sampled','time','dgsid','sampleid']].drop_duplicates('dgsid')
                 
    #Quality constant variables
    system_date=dt.date.today().strftime('%d-%b-%Y')
    
    #Remove duplicate flags from DGSIDs
    df['dgsid']=np.where(df.dgsid.str[-1:]=='D',df.dgsid.str[:-1],df.dgsid)
    
    df['SQL']=("""insert into quality (system_date,user_name,record_by,sam_method,agency,dgsid,\
    date_sampled,sampleid,time) values ('""")+system_date+"','"+\
        user_name+"','"+record_by+"','"+sam_method+"','"+agency+"','"+df['dgsid']+"','"+\
        df['date_sampled']+"','"+df['sampleid']+"','"+df['time']+"');"

    endpath=os.path.split(path)[0]    
    df.to_csv(endpath+'/quality_upload_'+file,index=False,columns=['SQL'])    