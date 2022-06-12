import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import csv
import json

def loadCCTVData(year, city):
    cctv_data= pd.read_csv('./CCTV현황(개방표준).csv')
    cctv_data=cctv_data.loc[(cctv_data['설치년월'].str.contains(str(year))==True)]
    cctv_data=cctv_data.loc[(cctv_data['소재지지번주소'].str.contains(city)==True)]
    return cctv_data


print(len(loadCCTVData(2017, '수원')))
print(len(loadCCTVData(2016, '수원')))