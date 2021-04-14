# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 14:03:22 2021

@author: mcquiggan
"""

#Charge balance from lab EDD
#Assumptions:
#1. Specific column names - Units, Parameters, DGSID, ReportingUnits, Results,
#2. Non detect values flagged with a 'ND'
#3. Alkalinity is changed to HCO3, but column header is not changed
#4. Parameter rows are looked up based on string containing certain text

import pandas as pd
import numpy as np
file='N:/Stormwater/Hydro_data/Lab WQ data/lab_field_reports/Feb2021eventEDD.csv'
df=pd.read_csv(file,na_values='ND')
df['Result']=pd.to_numeric(df.Result)

#Atomic weight
#Anions
ALK=100.086
CL=35.45
N3=62.004
N2=46.005
SO4=96.056
HCO3=61.016
#Cations
PB=207.2
NA=22.99
K=39.098
CA=40.078
FE=55.845
MG=24.305

#Valence
V_ALK=2
V_CL=1
V_N3=1
V_N2=1
V_SO4=2
V_HCO3=1
#Cations
V_PB=2
V_NA=1
V_K=1
V_CA=2
V_FE=2
V_MG=2


#New column for Results as mg/L
df['mgl']=df['Result']
df.loc[df['ReportingUnits']=='ug/L','mgl']=df['Result']/1000

#Pivot on site ID
df=df.pivot(index='Parameter', columns='DGSID',values='mgl')

#Assign rows by parameter, lookup phrase
ALK_ROW=np.where(df.index.str.contains('Alkalinity'))[0]
BR_ROW=np.where(df.index.str.contains('Bromide'))[0]
CA_ROW=np.where(df.index.str.contains('Calcium'))[0]
CL_ROW=np.where(df.index.str.contains('Chloride'))[0]
FE_ROW=np.where(df.index.str.contains('Iron'))[0]
MG_ROW=np.where(df.index.str.contains('Magnesium'))[0]
N3_ROW=np.where(df.index.str.contains('Nitrate'))[0]
N2_ROW=np.where(df.index.str.contains('Nitrite'))[0]
K_ROW=np.where(df.index.str.contains('Potassium'))[0]
NA_ROW=np.where(df.index.str.contains('Sodium'))[0]
SO4_ROW=np.where(df.index.str.contains('Sulfate'))[0]

#Convert mg/L to meq/L
df.iloc[ALK_ROW[0]]=((df.iloc[ALK_ROW[0]]/0.8202)*V_HCO3)/HCO3
df.iloc[CA_ROW[0]]=(df.iloc[CA_ROW[0]]*V_CA)/CA
df.iloc[CL_ROW[0]]=(df.iloc[CL_ROW[0]]*V_CL)/CL
df.iloc[FE_ROW[0]]=(df.iloc[FE_ROW[0]]*V_FE)/FE
df.iloc[MG_ROW[0]]=(df.iloc[MG_ROW[0]]*V_MG)/MG
df.iloc[N3_ROW[0]]=(df.iloc[N3_ROW[0]]*V_N3)/N3
df.iloc[N2_ROW[0]]=(df.iloc[N2_ROW[0]]*V_N2)/N2
df.iloc[K_ROW[0]]=(df.iloc[K_ROW[0]]*V_K)/K
df.iloc[NA_ROW[0]]=(df.iloc[NA_ROW[0]]*V_NA)/NA
df.iloc[SO4_ROW[0]]=(df.iloc[SO4_ROW[0]]*V_SO4)/SO4

dfcat=df.iloc[[NA_ROW[0],CA_ROW[0],K_ROW[0],FE_ROW[0],MG_ROW[0],ALK_ROW[0]],:]
dfans=df.iloc[[CL_ROW[0],N3_ROW[0],N2_ROW[0],SO4_ROW[0],ALK_ROW[0]],:]

total_cats=list(dfcat.sum())
total_ans=list(dfans.sum())
dgsid=list(df)

cbdf=pd.DataFrame(columns=['DGSID','Cations','Anions','CBE'])
cbdf['DGSID']=dgsid
cbdf['Cations']=total_cats
cbdf['Anions']=total_ans
cbdf['CBE']=abs(cbdf['Cations']-cbdf['Anions'])/(cbdf['Cations']+cbdf['Anions'])*100
cbdf.to_csv('N:/Stormwater/Hydro_data/Lab WQ data/Chg_bal_Feb2021.csv',index=False)








