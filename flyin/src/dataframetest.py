import pandas as pd
from  datetime import date
pd.set_option('display.width', 1500)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 50)

def CPT(esd):
    today=str(date.today())
    if(esd == today):
        result="CPT"
    else:
        result="Non CPT"

    return result




datasheet=pd.read_excel("D:\\Neha\\Amazon\\Faast\\rodeo.xlsx")
datasheet=datasheet.sort_values(['Expected Ship Date','Dwell Time (hours)'],ascending=[1,0])
datasheet=datasheet.loc[datasheet['Dwell Time (hours)']>0]
#datasheet=datasheet.loc[datasheet['Outer Scannable ID'] != 'pmP-1-V']
datasheet['Location']="Dubai"
datasheet['Status']=""

datasheet['Con Date']=datasheet['Expected Ship Date'].dt.date

for index,row in datasheet.iterrows():
    a=CPT(str(row['Con Date']))
    datasheet.iloc[index,-2]=a


print(datasheet)