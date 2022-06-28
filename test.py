import pandas as pd
import csv
import json

def loadCrimeData():
    global crime_data
    crime_data= pd.read_csv('./범죄_발생지_2017~2020.csv', encoding = 'cp949')

def loadBellData(year, city):
    emergency_bell_data= pd.read_csv('./안전비상벨위치현황(개방표준).csv', encoding = 'cp949')
    emergency_bell_data=emergency_bell_data.loc[(emergency_bell_data['안전비상벨설치년도']==year)]
    emergency_bell_data=emergency_bell_data.loc[(emergency_bell_data['소재지지번주소'].str.contains(city))]
    return emergency_bell_data

def loadCCTVData(year, city):
    cctv_data= pd.read_csv('./CCTV현황(개방표준).csv')
    cctv_data=cctv_data.loc[(cctv_data['설치년월'].str.contains(str(year))==True)]
    cctv_data=cctv_data.loc[(cctv_data['소재지지번주소'].str.contains(city)==True)]
    return cctv_data

def loadPoliceData(year, city):
    datas = dict()
    with open('./경찰청_경찰서별정원_20211014.csv',encoding='cp949') as f:
        data = csv.reader(f)
        for row in data:
            if str(year-1)+'년' in row or str(year)+'년' in row:
                ps = row[2]
                if ps not in datas:
                    datas[ps] = dict()
                datas[ps]['addr'] = row[3]
                datas[ps][row[0]] = int(row[4].replace(',', ''))

    results = []
    for ps in datas:
        if len(datas[ps]) < 3: continue
        p_2016 = datas[ps][str(year-1)+'년']
        p_2017 = datas[ps][str(year)+'년']
        var = p_2017 - p_2016
        var_rate = round(var / p_2016 * 100, 4)
        if abs(var) < 0: continue  # 증감이 몇 이상인 데이터만 뽑아오도록 결정하는 부분
        results.append([ps, datas[ps]['addr'], var, var_rate])

    with open('result.csv', 'w', newline='') as f:
        new_data = csv.writer(f)
        new_data.writerow(['경찰서', '주소', '인원증감', '증감율'])
        new_data.writerows(results)

    result_data = pd.read_csv('./result.csv', encoding='euc-kr')  # author: 가희. 환경 마다 인코딩 에러가 날수 있어서 encoding='cp949' 추가함
    police_data =result_data[result_data['주소'].str.contains(city)].reset_index(drop=True)

    return police_data

def getCrimeData(year):
    data= pd.read_csv('./범죄_발생지_2017~2020.csv', encoding = 'cp949')

    data1=data.iloc[:,0:39]
    data2=data.iloc[:,99:127]
    data1 = pd.concat([data1, data2],axis=1)
    # print(data1)
    crime_data= data1.drop(data1.columns[[2,3,4,5,6,7,8,9,10]], axis=1)

    one =crime_data['죄종별(1)'].isin(['노동범죄', '안보범죄','선거범죄','병역범죄','기타범죄','계'])
    crime_data=crime_data[~one] 

    two =crime_data['죄종별(2)'].isin(['소계','죄종별(2)'])
    crime_data=crime_data[two]

    crime_data=crime_data.iloc[1:] 

    crime_data = crime_data.rename(columns=crime_data.iloc[0])

    crime_data=crime_data.drop(1,axis=0)

    crime_data=crime_data.reset_index(drop=True)

    crime_2017=crime_data.iloc[:,0:30]
    crime_2018=pd.concat([crime_data.iloc[:,0:2], crime_data.iloc[:,30:]], axis=1)

    if year==2017:
        return crime_2017
    elif year==2018:
        return crime_2018


city='경기'

crime_counts=[409122, 381295, 385160, 383565]
cctv_counts=[2565, 3932, 3679, 289]
bell_counts=[1733, 863, 1257, 59]

policeman_counts=[len(loadPoliceData(2017,city)), len(loadPoliceData(2018,city)), len(loadPoliceData(2019,city)), len(loadPoliceData(2020,city))]
print(policeman_counts)