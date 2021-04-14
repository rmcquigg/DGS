# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 13:20:49 2021

@author: mcquiggan
"""
import pandas as pd
import matplotlib.pyplot as plt

#File specified below should be a csv saved from the query15.xlsx workbook 
#Edit query directly to change well
file='S:/Common/DATA/WATLEV/troll_unc/PreProcess/freshwater_head/query15.csv'
#List DGSID and screen mid-point elevation (in ft NAV88)
dgsid='Ie32-05'
mp_elev=3.8
screen_elev=3.8

#Read in csv file as a dataframe and rename some columns
df=pd.read_csv(file)
df.rename(columns={'MSMT_TIME':'DateTime',"'"+dgsid+"'_'W'":'LEVEL',"'"+dgsid+"'_'C'":'SCON',"'"+dgsid+"'_'T'":'TEMP'},inplace=True)
df['ELEV']=mp_elev-df['LEVEL']
scon=df['SCON']

#Use this value for sw where sensor elev unknown or when sensor goes dry periodically
sw_base_elev=min(df['ELEV'])
df['HEIGHT']=df['LEVEL']-sw_base_elev

#Use this for wells where screen elev is known or sw mp is same as sensor elev
df['HEIGHT']=df['LEVEL']-screen_elev

#Calcs
p=(scon/50000)*(1025-1000)+1000
df['p']=(scon/50000)*(1025-1000)+1000
df['HEIGHT_FEH']=round(df['HEIGHT']*(df['p']/1000),2)
df['ELEV_FEH']=round(df['ELEV']+(df['HEIGHT_FEH']-df['HEIGHT']),2)

#Elevation difference in feet (SWs will be negative)
y=df['ELEV_FEH']
y1=df['ELEV']
diff=round((y1-y),2)
mindiff=min(diff)
maxdiff=max(diff)
meandiff=diff.sum()/len(diff.dropna())
#Differnce as a percentage
y2=abs(round(((y1-y)/y1)*100,2))

#df to csv, just elevation
df.to_csv('S:/Common/DATA/WATLEV/troll_unc/PreProcess/freshwater_head/output/'+dgsid+'.csv',columns=['DateTime','SCON','LEVEL','ELEV','ELEV_FEH'],index=False)

#Plot and save figure as a .png
x=pd.to_datetime(df['DateTime'])
fig,(ax,ax1)=plt.subplots(1,2,figsize=(12,4))
ax.plot(x,y,marker='^',markersize=5,linestyle='None',label='Freshwater Level')
ax.plot(x,y1,marker='.',markersize=5,linestyle='None',label='Original Level')
ax1.scatter(scon,diff,marker='.')
ax1.set_xlabel('SC in uS/cm')
ax1.set_ylabel('feet decrease in elevation')
ax.tick_params(axis='x',labelrotation=45)
ax.legend()
#ax.invert_yaxis()
fig.savefig('S:/Common/DATA/WATLEV/troll_unc/PreProcess/freshwater_head/output/'+dgsid+'.png')



