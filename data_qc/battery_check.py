# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 09:04:52 2021
@author: mcquiggan
"""
import csv
import pandas as pd
import os

def bat_life(path):
    if os.path.exists(path+'/bat_life_check.csv'):
        os.remove(path+'/bat_life_check.csv')
    sn=[]
    batt=[]
    date=[]
    well=[]
    for each in os.scandir(path):
        try:
            dgsid=each.name.split(sep='_')[0]
            well.append(dgsid)
            with open(each,'r',encoding='utf8',errors='ignore') as f:
                csv.reader(f)
                for i,row in enumerate(f):
                    if i==0:
                        dat=row.split(sep=',')[1]
                        date.append(dat.rstrip())
                    if i==15:
                        no=row.split(sep=',')[1]
                        sn.append(no.rstrip())
                    if i==21:
                        used=(100-int(row.split(sep=',')[1]))
                        batt.append(str(used)+' %')
               
        except:
            pass
    df=pd.DataFrame(columns=('sn','batt','date','well'))
    df['sn']=sn
    df['batt']=batt
    df['date']=date
    df['well']=well
    df.to_csv(path+'/bat_life_check.csv',index=False)
    

path='S:/Common/DATA/WATLEV/troll_unc/PreProcess/temp'
bat_life(path)
