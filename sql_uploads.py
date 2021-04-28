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

def tests(path,agency,test_source,user_name):
    
    df=pd.read_csv(path)
    
    #This is specifically for DNREC ELS lab EDDs
    df=df.drop(['CustomerName','ProjectName','OrderID','ELSSampleNumber','Site','Matrix',
                'Analysis Time','LOQ','FieldQC','Dilution','Qualifier'],axis=1)
    df=df.rename(columns={'ReportingUnits':'units','Parameter':'test','Collect Date':'date_sampled',
                          'Collect Time':'time','Analysis Date':'date_analyzed','Method':'test_method'})
    #Change parameter names to Watsys test codes
    from functools import reduce
    dc={'Potassium, Dissolved':'K','Iron, Dissolved':'FED','Chloride, Dissolved':'CL','Silica, Dissolved':'SI',
        'Nitrate as N, Dissolved':'N2','Nitrite as N, Dissolved':'N3','Magnesium, Dissolved':'MG',
        'Bromide, Dissolved':'BR','Alkalinity (Titrimetric, pH 4.5), Dissolved':'ALK','Sulfate, Dissolved':'SO4',
        'Sodium, Dissolved':'NA','Nitrate/Nitrite as N, Dissolved':'NT','Residue, Filterable (TDS)':'TDS',
        'Calcium, Dissolved':'CA'}
    df['test']=reduce(lambda x, y: x.replace(y,dc[y]),dc,df['test'])
    #Another way to run through the dict
    # par=df['test']
    # test=[]
    # for p in par:
    #     test.append(dc.get(p,p))
    
    #Change test methods to Watsys codes
    methdc={'ALK':'SM2320',
            'AS':'EPA200.8',
            'CD':'EPA200.8',
            'CA':'EPA200.7',
            'CL':'SM4500CL',
            'CR':'EPA200.8',
            'CU':'EPA200.8',
            'FED':'EPA200.7',
            'PB':'EPA200.8',
            'MG':'EPA200.8',
            'HG':'EPA245.1',
            'N23':'EPA353.2',
            'N3':'EPA353.2',
            'N2':'EPA353.2',
            'K':'EPA200.7',
            'NA':'EPA200.7',
            'TDS':'SM2540C',
            'SO4':'EPA300.0',
            'FE':'EPA200.7',
            'NT':'EPA353.2',
            'TSS':'SM2450',
            'TE':'EPA170.1',
            'SC':'EPA120.1',
            'PH':'EPA150.1',
            'NAM':'SM4500',
            'COD':'EPA410.4',
            'BR':'EPA300.0',
            'AL':'EPA200.8',
            'SI':'SM4500SIO2C',
            'DO':'EPA360.1'}
    df['test_method']=reduce(lambda x, y: x.replace(y,methdc[y]),methdc,df['test'])
    
    
    df['dgsid']='Fb31-'+(df['CustomerSampleNumber']).astype(str)
    df['amount']=np.where(df['Result']=='ND',df['MDL'],df['Result'])
    df['amount']=np.where(df['units']=='ug/L',(df['amount']).astype(float)/1000,df['amount'])
    df['units']='M'
    df['units']=np.where(df['Result']=='ND','LM',df['units'])
    df['date_sampled']=pd.to_datetime(df['date_sampled']).dt.strftime('%m/%d/%Y')
    df['date_analyzed']=pd.to_datetime(df['date_analyzed']).dt.strftime('%y%m%d')
    #Only run next statement if there any blanks in date_analyzed
    #df['date_analyzed'] = df['date_analyzed'].replace('NaT','')
    df['time']=pd.to_datetime(df['time']).dt.strftime('%H%M')
    df=df.assign(sampleid=lambda df:df['date_sampled']+df['dgsid']+'G',
              testid= lambda df:df['date_sampled']+df['dgsid']+df['test'])
    df=df.drop(['CustomerSampleNumber','MDL','Result'],axis=1)
    
    system_date=dt.date.today().strftime('%d-%b-%Y')
    
    df['SQL']=("""insert into tests (system_date,user_name,test_source,agency,dgsid,date_sampled,\
    sampleid,date_analyzed,test,testid,test_method,units,amount) values ('""")+system_date+"','"+\
        user_name+"','"+test_source+"','"+agency+"','"+df['dgsid']+"','"+\
        df['date_sampled']+"','"+df['sampleid']+"','"+df['date_analyzed']+"','"+\
        df['test']+"','"+df['testid']+"','"+df['test_method']+"','"+df['units']+"',"+\
        df['amount'].astype(str)+");"
    endpath=os.path.split(path)[0]    
    df.to_csv(endpath+'/tests_upload.csv',index=False,columns=['SQL'])
    
def quality(path,agency,user_name,record_by,sam_method):
    
    df=pd.read_csv(path)
    
    #This is specifically for DNREC ELS lab EDDs
    df=df.drop(['CustomerName','ProjectName','OrderID','ELSSampleNumber','Site','Matrix',
                'Analysis Time','LOQ','FieldQC','Dilution','Qualifier','Result','ReportingUnits',
                'Parameter','Analysis Date','MDL'],axis=1)
    df=df.rename(columns={'Collect Date':'date_sampled',
                          'Collect Time':'time','Method':'test_method'})
        
    df['dgsid']='Fb31-'+(df['CustomerSampleNumber']).astype(str)
    df['date_sampled']=pd.to_datetime(df['date_sampled']).dt.strftime('%m/%d/%Y')
    df['time']=pd.to_datetime(df['time']).dt.strftime('%H%M')
    df=df.assign(sampleid=lambda df:df['date_sampled']+df['dgsid']+'G')
    df=df.drop(['CustomerSampleNumber'],axis=1)
    
    df['system_date']=dt.date.today().strftime('%d-%b-%Y')
   
    df=df[['date_sampled','time','dgsid','sampleid']].drop_duplicates('dgsid')
                 
    #Quality constant variables
    system_date=dt.date.today().strftime('%d-%b-%Y')
    
    df['SQL']=("""insert into quality (system_date,user_name,record_by,sam_method,agency,dgsid,\
    date_sampled,sampleid,time) values ('""")+system_date+"','"+\
        user_name+"','"+record_by+"','"+sam_method+"','"+agency+"','"+df['dgsid']+"','"+\
        df['date_sampled']+"','"+df['sampleid']+"','"+df['time']+"');"
    endpath=os.path.split(path)[0]    
    df.to_csv(endpath+'/quality_upload.csv',index=False,columns=['SQL'])    