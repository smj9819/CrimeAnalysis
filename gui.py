from tkinter import *
from tkinter import ttk
import tkintermapview
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd
import csv
import json


plt.rc('font', family='NanumGothic.ttf')

def loadCrimeData():
    global crime_data
    crime_data= pd.read_csv('./범죄_발생지_2017~2020.csv', encoding = 'cp949')
    # print(crime_data.head())

def loadBellData():
    global emergency_bell_data
    emergency_bell_data= pd.read_csv('./안전비상벨위치현황(개방표준).csv', encoding = 'cp949')
    emergency_bell_data=emergency_bell_data.loc[(emergency_bell_data['안전비상벨설치년도']==2017)]
    emergency_bell_data=emergency_bell_data.loc[(emergency_bell_data['소재지지번주소'].str.contains('경기도'))]
    # print(emergency_bell_data.head())

def loadCCTVData():
    global cctv_data
    cctv_data= pd.read_csv('./CCTV현황(개방표준).csv')
    cctv_data=cctv_data.loc[(cctv_data['설치년월'].str.contains('2017')==True)]
    cctv_data=cctv_data.loc[(cctv_data['소재지지번주소'].str.contains('경기도')==True)]
    # print(cctv_data.head())

def loadPoliceData():
    global police_data

    datas = dict()
    with open('./경찰청_경찰서별정원_20211014.csv',encoding='cp949') as f:
        data = csv.reader(f)
        for row in data:
            if '2016년' in row or '2017년' in row:
                ps = row[2]
                if ps not in datas:
                    datas[ps] = dict()
                datas[ps]['addr'] = row[3]
                datas[ps][row[0]] = int(row[4].replace(',', ''))

    results = []
    for ps in datas:
        if len(datas[ps]) < 3: continue
        p_2016 = datas[ps]['2016년']
        p_2017 = datas[ps]['2017년']
        var = p_2017 - p_2016
        var_rate = round(var / p_2016 * 100, 4)
        if abs(var) < 0: continue  # 증감이 몇 이상인 데이터만 뽑아오도록 결정하는 부분
        results.append([ps, datas[ps]['addr'], var, var_rate])

    with open('result.csv', 'w', newline='') as f:
        new_data = csv.writer(f)
        new_data.writerow(['경찰서', '주소', '인원증감', '증감율'])
        new_data.writerows(results)

    result_data = pd.read_csv('./result.csv', encoding='euc-kr')  # author: 가희. 환경 마다 인코딩 에러가 날수 있어서 encoding='cp949' 추가함
    police_data =result_data[result_data['주소'].str.contains('경기도')].reset_index(drop=True)
    # print(police_data.head())

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

def saveCrimeCountGraph():
    global temp_2017

    temp=getCrimeData(2017)
    # Basic stacked area chart.
    x=temp.columns[2:]
    y_list=[]

    summations=[]
    cities=temp.columns[2:]

    for i in range(10):
        y=list(temp.iloc[i])[2:]
        y_list.append([int(i) for i in y])

    for city in cities:
        y=temp[city]
        summations.append(sum([int(i) for i in y]))

    temp_2017=pd.DataFrame({'City':x, 'Counts':summations})
    temp_2017=temp_2017.sort_values(['Counts','City'], ascending=True)
    # print(temp_2017)

    plt.barh(range(len(x)), list(temp_2017['Counts']))

    ax = plt.gca()
    ax.axes.xaxis.set_visible(False)
    ax.axes.xaxis.set_ticks([])

    plt.gca().spines['right'].set_visible(False) #오른쪽 테두리 제거
    plt.gca().spines['top'].set_visible(False) #위 테두리 제거
    plt.gca().spines['left'].set_visible(False) #왼쪽 테두리 제거
    plt.gca().spines['bottom'].set_visible(False) #아래쪽 테두리 제거

    # plt.title('Total crime counts by city', fontsize=18)
    # plt.ylabel('City', fontsize=15)
    # plt.xlabel('Crime counts', fontsize=15)
    plt.yticks(range(len(x)), list(temp_2017['City']), fontsize=10, rotation=0)
    plt.savefig('CrimeCounts.png', transparent=True, bbox_inches = 'tight')

def saveCorrGraph():
    global corr_result

    crime_counts=[409122, 381295, 385160, 383565]
    cctv_counts=[2565, 3932, 3679, 289]
    bell_counts=[1733, 863, 1257, 59]
    policeman_counts=[539, 148, 300, 45]

    data=pd.DataFrame({'CCTV':cctv_counts, 'Bell':bell_counts, 'PoliceMan':policeman_counts, 'Crime':crime_counts}, index=[2017,2018,2019,2020])
    corr_result=data.corr(method='spearman')

    sns.pairplot(data,hue='Crime')
    plt.savefig('pairplot.png', transparent=True)

saveCrimeCountGraph()
saveCorrGraph()


def getCrimeDifference(city1):
    global crime_difference

    # 2018 범죄 건수 - 2017 범죄 건수
    crime_difference=getCrimeData(2017).iloc[:,0]

    temp_2017=getCrimeData(2017).iloc[:,2:]
    temp_2018=getCrimeData(2018).iloc[:,2:]

    cities=temp_2018.columns[:]

    d1=[]
    d2=[]
    for city in cities:
        d1.append(temp_2018[city].replace('-','0').astype(int))
        d2.append(temp_2017[city].replace('-','0').astype(int))

    temp_2018=pd.concat(d1,axis=1)
    temp_2017=pd.concat(d2,axis=1)

    crime_difference=pd.concat([crime_difference,temp_2018-temp_2017],axis=1)
    # print(crime_difference)


getCrimeDifference()

def polygon_click(polygon):
    current_city.set(polygon.name+' 범죄 발생 통계')

root = Tk()

root.title("5조 데분기 과제 산출물")
root.geometry("1800x1200")
# root.configure(bg='white')
root.resizable(False, False)

frm1 = ttk.Frame(root, padding=30)

frm1_1=ttk.Frame(frm1, padding=0)
ttk.Label(frm1_1, text="데이터 분석 기초 5조 팀프로젝트", font=("Times","14","bold")).grid(column=0, row=0, columnspan=2, sticky=W)
ttk.Label(frm1_1, text="범죄예방시설물의 영향도 분석", font=("Times","14","bold")).grid(column=0, row=1,columnspan=2, sticky=W)
ttk.Label(frm1_1, text=" ").grid(column=0, row=2,columnspan=2, sticky=W)
ttk.Label(frm1_1, text="팀원").grid(column=0, row=3, sticky=W)
ttk.Label(frm1_1, text="강동영, 김우석, 김영준, 소문주, 조가희").grid(column=1, row=3, sticky=W)
frm1_1.place(height=100, width=400, x=0,y=0)

frm1_2 = ttk.Frame(frm1, padding=0)
ttk.Label(frm1_2, text="\n시별 범죄 발생률(기준: 2017년도)", font=("Times","12","bold")).pack(anchor="w")
image=PhotoImage(file="CrimeCounts.png")
label=ttk.Label(frm1_2, image=image)
label.pack(anchor="nw")
frm1_2.place(height=500, width=400, x=0, y=100)

frm1.place(height=600, width=400, x=0,y=0)


# 지도
frm2 = ttk.Frame(root, padding=30)
frm2.place(height=600, width=700, x=400, y=0)

map_widget=tkintermapview.TkinterMapView(frm2,width=700,height=500,corner_radius=0)
map_widget.set_position(37.394946, 127.111104)
map_widget.place(height=500, width=700, x=0, y=0)

gyeonggi_geojson='./TL_SCCO_SIG.json'

# for i in range(0,len(cctv_data),5):
#     # 이거 다 띄우면 화면에 버퍼링생김
#     # 일단 5개 마다 한개씩 띄움
#     map_widget.set_marker(cctv_data.iloc[i]['위도'], cctv_data.iloc[i]['경도'], text=cctv_data.iloc[i]['설치목적구분'])

gyeonggi_geojson='./TL_SCCO_SIG.json'

with open(gyeonggi_geojson, 'r', encoding='utf-8') as file:
    data = json.load(file)

colors=["green", "orange", "orangered1","orangered4"]
for feature in data["features"]:
    city = feature["properties"]["SIG_KOR_NM"]

    for coords in feature["geometry"]["coordinates"]:
        # print(coords)
        for coord in coords:
            coord[0], coord[1]=coord[1], coord[0]

        cnt=temp_2017.loc[(temp_2017['City'] == city)]['Counts']
        if len(cnt)==0:
            polygon_1 = map_widget.set_polygon(coords,
                                   fill_color=colors[0],
                                   # outline_color="red",
                                   border_width=1,
                                   command=polygon_click,
                                   name=city)
        else:
            polygon_1 = map_widget.set_polygon(coords,
                                   fill_color=colors[list(cnt)[0]//10000],
                                   # outline_color="red",
                                   border_width=1,
                                   command=polygon_click,
                                   name=city)

    
map_widget.set_zoom(10)
map_widget.pack()

frm2_1=ttk.Frame(frm2,padding=10)

CheckVar1=IntVar()
CheckVar2=IntVar()
CheckVar3=IntVar()

c1=Checkbutton(frm2_1,text="CCTV",variable=CheckVar1)
c1.grid(column=0, row=0)
c2=Checkbutton(frm2_1,text="안전벨",variable=CheckVar2)
c2.grid(column=1, row=0)
c3=Checkbutton(frm2_1,text="경찰서",variable=CheckVar3)
c3.grid(column=2, row=0)

RadioVariety=IntVar()

def ok():                
    if RadioVariety.get() == 1:

        str = "Radio 1 selected"
    if RadioVariety.get() == 2:
        str = "Radio 2 selected"
 

radio1=Radiobutton(frm2_1, text="경찰관 수", value=1, variable=RadioVariety, command=ok)
radio1.grid(column=3, row=0)
radio2=Radiobutton(frm2_1, text="범죄 발생 건수", value=2, variable=RadioVariety, command=ok)
radio2.grid(column=4, row=0)


frm2_1.pack()
frm2_1.place(height=100, width=600, x=0, y=500)






current_city = StringVar()
current_city.set('---')

frm4=ttk.Frame(root, padding=30)
selected_city_name=ttk.Label(frm4, textvariable=current_city, font=("Times","14","bold"))
selected_city_name.pack(anchor="w")

plt.clf()
fig, ax=plt.subplots(1,2)
fig.tight_layout(pad=3.0)

ratio = [34, 32, 16, 18]
labels = ['Apple', 'Banana', 'Melon', 'Grapes']
ax[0].pie(ratio, labels=labels, autopct='%.1f%%')
ax[0].set_title('2017 범죄 분포')

ratio = [34, 32, 16, 18]
labels = ['Apple', 'Banana', 'Melon', 'Grapes']
ax[1].pie(ratio, labels=labels, autopct='%.1f%%')
ax[1].set_title('2018 범죄 분포')

canvas = FigureCanvasTkAgg(fig, master=frm4)
canvas.draw()
canvas.get_tk_widget().pack(anchor="w")

# image=PhotoImage(file="pairplot.png")
# label=ttk.Label(frm4, image=image)
# label.pack(anchor="w")
frm4.place(height=600, width=700, x=1100, y=0)


frm6 = ttk.Frame(root, padding=30)
print(crime_difference)
ttk.Label(frm6, text="").grid(column=0, row=0)

idxs=list(crime_difference.index)
cols=list(crime_difference.columns)
for i in range(len(crime_difference.columns)):
    ttk.Label(frm6, text=cols[i], font=("Times","14","bold")).grid(column=i+1, row=0, sticky=W)

for j in range(len(idxs)):
    ttk.Label(frm6, text=idxs[j], font=("Times","14","bold")).grid(column=0, row=j+1, sticky=W)
    for i in range(len(cols)):
        ttk.Label(frm6, text=str(crime_difference.at[idxs[j],cols[i]]), font=("Times","14")).grid(column=i+1, row=j+1, sticky=W)

# ttk.Label(frm6, text="", font=("Times","14")).grid(column=0, row=5, columnspan=5, sticky=W)
# ttk.Label(frm6, text="범죄율과 가장 상관관계가 높은 항목은 경찰관, 안전벨입니다", font=("Times","14")).grid(column=0, row=6, columnspan=5, sticky=W)
# ttk.Label(frm6, text="범죄율과 가장 상관관계가 낮은 항목은 CCTV입니다", font=("Times","14")).grid(column=0, row=7, columnspan=5, sticky=W)
frm6.place(height=600, width=1100, x=0, y=600)


frm5 = ttk.Frame(root, padding=30)
listOfIndex=list(corr_result.index)
print(listOfIndex)
ttk.Label(frm5, text="").grid(column=0, row=0)
for i in range(len(listOfIndex)):
    ttk.Label(frm5, text=listOfIndex[i], font=("Times","14","bold")).grid(column=i+1, row=0, sticky=W)

for j in range(len(listOfIndex)):
    ttk.Label(frm5, text=listOfIndex[j], font=("Times","14","bold")).grid(column=0, row=j+1, sticky=W)
    for i in range(len(listOfIndex)):
        ttk.Label(frm5, text=str(corr_result.at[listOfIndex[j],listOfIndex[i]]), font=("Times","14")).grid(column=i+1, row=j+1, sticky=W)

ttk.Label(frm5, text="", font=("Times","14")).grid(column=0, row=5, columnspan=5, sticky=W)
ttk.Label(frm5, text="범죄율과 가장 상관관계가 높은 항목은 경찰관, 안전벨입니다", font=("Times","14")).grid(column=0, row=6, columnspan=5, sticky=W)
ttk.Label(frm5, text="범죄율과 가장 상관관계가 낮은 항목은 CCTV입니다", font=("Times","14")).grid(column=0, row=7, columnspan=5, sticky=W)


frm5.place(height=600, width=700, x=1100,y=600)


root.mainloop()