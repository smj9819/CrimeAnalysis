from tkinter import *
from tkinter import ttk
import tkintermapview
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import seaborn as sns

import pandas as pd
import csv
import json

path = 'NanumGothic.ttf'
font_name = fm.FontProperties(fname=path).get_name()
print(font_name)
plt.rc('font', family=font_name)

def loadCrimeData():
    global crime_data
    crime_data= pd.read_csv('./범죄_발생지_2017~2020.csv', encoding = 'cp949')
    # print(crime_data.head())

def loadBellData(city):
    emergency_bell_data= pd.read_csv('./안전비상벨위치현황(개방표준).csv', encoding = 'cp949')
    emergency_bell_data=emergency_bell_data.loc[(emergency_bell_data['안전비상벨설치년도']==2017)]
    emergency_bell_data=emergency_bell_data.loc[(emergency_bell_data['소재지지번주소'].str.contains(city))]
    return emergency_bell_data

def loadCCTVData(city):
    cctv_data= pd.read_csv('./CCTV현황(개방표준).csv')
    cctv_data=cctv_data.loc[(cctv_data['설치년월'].str.contains('2017')==True)]
    cctv_data=cctv_data.loc[(cctv_data['소재지지번주소'].str.contains(city)==True)]
    return cctv_data

def loadPoliceData(city):
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

def saveCrimeCountGraph():
    global temp_2017

    temp=getCrimeData(2017)
    # Basic stacked area chart.
    x=temp.columns[2:]
    y_list=[]

    summations=[]
    cities=temp.columns[2:]
    bar_colors=[]

    for i in range(10):
        y=list(temp.iloc[i])[2:]
        y_list.append([int(i) for i in y])

    for city in cities:
        y=temp[city]
        summations.append(sum([int(i) for i in y]))
        bar_colors.append('blue')

    bar_colors[len(bar_colors)-1]='red'

    temp_2017=pd.DataFrame({'City':x, 'Counts':summations})
    temp_2017=temp_2017.sort_values(['Counts','City'], ascending=True)

    plt.barh(range(len(x)), list(temp_2017['Counts']), color=bar_colors)

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

    # plt.clf()
    # plt.bar(range(3),[cctv_counts[0],bell_counts[0], policeman_counts[0]], label=['CCTV','Bell','PoliceMan'])
    # plt.savefig('FaciDiff.png', transparent=True, bbox_inches = 'tight')

    data=pd.DataFrame({'CCTV':cctv_counts, 'Bell':bell_counts, 'PoliceMan':policeman_counts, 'Crime':crime_counts}, index=[2017,2018,2019,2020])
    corr_result=data.corr(method='pearson')

    corr_result=corr_result.round(2)
    sns.pairplot(data)
    plt.savefig('pairplot.png', transparent=True)

saveCrimeCountGraph()
saveCorrGraph()


def getCrimeDifference(city):
    global crime_difference

    # 2018 범죄 건수 - 2017 범죄 건수
    crime_difference=getCrimeData(2017).iloc[:,0].tolist()

    d1=getCrimeData(2017)[city].replace('-','0').astype(int).values
    d2=getCrimeData(2018)[city].replace('-','0').astype(int).values
    d3=[]

    for i in range(len(d1)):
        d3.append(d2[i]-d1[i])

    crime_difference=pd.DataFrame({'2017':d1,'2018':d2, 'Crime Diff':d3},index=crime_difference)


    plt.clf()
    plt.bar(range(len(crime_difference)),d3,label=crime_difference)
    plt.savefig('Crime_difference.png', transparent=True, bbox_inches = 'tight')

    return crime_difference

getCrimeDifference('수원시')

def saveCrimePieChart(city):
    crime_diff=getCrimeDifference('수원시')
    # plt.clf()
    # plt.subplot(1,2,1)
    # plt.pie(crime_diff['2017'].tolist(),
    #          labels=list(crime_diff.index),
    #          startangle=90,
    #          counterclock=True,
    #          autopct=lambda p: '{:.2f}%'.format(p))
    # # plt.savefig('Crime2017.png', transparent=True, bbox_inches = 'tight')

    # plt.subplot(1,2,2)
    # plt.pie(crime_diff['2018'].tolist(),
    #          labels=list(crime_diff.index),
    #          startangle=90,
    #          counterclock=True,
    #          autopct=lambda p: '{:.2f}%'.format(p))
    # plt.savefig('Crime_2017_2018.png', transparent=True, bbox_inches = 'tight')

    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(5, 3)

    year2017=list(crime_diff['2017'].values) # [672,5494,7919,7973,595,1133,158,318,32,14266]
    year2018=list(crime_diff['2018'].values) # [637,5381,8071,8723,613,1131,98,355,35,11159]

    results={
        '2017':year2017,
        '2018':year2018
    }

    data=np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_names = ['강력','절도','폭력','지능','풍속','특별경제','마약','보건','환경','교통']

    plt.gca().set_xlim(0, max(np.sum(year2017), np.sum(year2018)))

    for i, colname in enumerate(zip(category_names)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = plt.barh(['2017','2018'], widths, left=starts, height=0.4,
                        label=category_names[i])

    plt.title("Crime ratio, amount in 2017-2018", fontsize=14)
    plt.legend(loc="lower left", ncol=len(category_names)//2)
    plt.savefig('Crime_2017_2018_2.png', dpi=100, transparent=True, bbox_inches = 'tight')

saveCrimePieChart('수원시')

def saveFacilitiesGraph():
    # TODO: 문주님
    # 전처리 데이터프레임 객체 값 -> df = pd.DataFrame([[124, 55, 122],[444, 22, 555]]) 라면

    # 피쳐 - 전처리 된 데이터프레임 객체 컬럼 별 선택 (numpy array든 파이썬 list)
    Y_cctv = [100, 400]  # df['CCTV']
    Y_bell = [5555, 2325] # df['BELL']
    Y_police = [125412, 24142] # df['POLICE']
    Y_crime = [80909, 12141] # df['CRIME']

    #  figure 전체를 컨트롤하는 변수와 그래프 각각을 조절할 수 있는 변수
    f, axes = plt.subplots(1, 3)

    # 격자 크기 설정
    f.set_size_inches((16, 5))

    # 서브플롯들 X축은 모두 17' 18' 년도
    x = ['2017', '2018']

    axes[0].bar(x, Y_cctv, color = ['black', 'g'], alpha = 0.4, width=0.4)
    axes[0].set_title("CCTV Trend", fontsize=14)
    # axes[0].set_ylabel("count", fontsize=14)
    # axes[0].set_xlabel("year", fontsize=14)

    axes[1].bar(x, Y_bell, color = ['black', 'g'], alpha = 0.4, width=0.4)
    axes[1].set_title("Bell Trend", fontsize=14)
    # axes[1].set_xlabel("year", fontsize=14)

    axes[2].bar(x, Y_police, color = ['black', 'g'], alpha = 0.4, width=0.4)
    axes[2].set_title("Police Trend", fontsize=14)
    # axes[2].set_xlabel("year", fontsize=14)

    # axes[3].bar(x, Y_crime, color = ['black', 'g'], alpha = 0.4, width=0.4)
    # axes[3].set_title("Crime Trend", fontsize=14)
    # axes[3].set_xlabel("year", fontsize=14)
    
    fig = plt.gcf()
    fig.set_size_inches(6, 4)
    plt.savefig('FaciDiff.png', dpi=100, transparent=True, bbox_inches = 'tight')

saveFacilitiesGraph()

def polygon_click(polygon):
    print('cliekced', polygon.name)
    current_city.set(polygon.name+' 범죄 발생 통계')

root = Tk()

root.title("5조 데분기 과제 산출물")
root.geometry("1800x1100")
# root.configure(bg='white')
root.resizable(False, False)

frm1 = ttk.Frame(root, padding=30)

frm1_1=ttk.Frame(frm1, padding=0)
ttk.Label(frm1_1, text="데이터 분석 기초 5조 팀프로젝트", font=("Times","14","bold")).grid(column=0, row=0, columnspan=2, sticky=W)
ttk.Label(frm1_1, text="범죄예방시설물의 영향도 분석", font=("Times","14","bold")).grid(column=0, row=1,columnspan=2, sticky=W)
ttk.Label(frm1_1, text=" ").grid(column=0, row=2,columnspan=2, sticky=W)
ttk.Label(frm1_1, text="팀원").grid(column=0, row=3, sticky=W)
ttk.Label(frm1_1, text="강동영, 김우석, 김영준, 소문주, 조가희").grid(column=1, row=3, sticky=W)
frm1_1.place(height=100, width=420, x=0,y=0)

frm1_2 = ttk.Frame(frm1, padding=0)
ttk.Label(frm1_2, text="\n시별 범죄 발생률(기준: 2017년도)", font=("Times","12","bold")).pack(anchor="w")
image=PhotoImage(file="CrimeCounts.png",master=frm1_2)
label=ttk.Label(frm1_2, image=image)
label.pack(anchor="nw")
frm1_2.place(height=450, width=420, x=0, y=100)
frm1.place(height=550, width=420, x=0,y=0)


frm2 = ttk.Frame(root, padding=30)
frm2.place(height=550, width=1350, x=420, y=0)

frm2_1 = ttk.Frame(frm2, padding=0)
map_widget=tkintermapview.TkinterMapView(frm2_1,height=550,width=1350,corner_radius=0)
map_widget.set_position(37.394946, 127.111104)
map_widget.place(height=550, width=1350, x=0, y=0)

gyeonggi_geojson='./TL_SCCO_SIG.json'

with open(gyeonggi_geojson, 'r', encoding='utf-8') as file:
    data = json.load(file)

map_widget.set_zoom(10)
map_widget.pack()
frm2_1.place(height=550, width=1350, x=0, y=0)



# frm2_2_1_2=ttk.Frame(frm2_2_1, padding=0)
# frm2_2_1_2.place(height=500, width=600, x=0, y=50)
# image1=PhotoImage(file="Crime_2017_2018_2.png",master=frm2_2_1_2)
# label=ttk.Label(frm2_2_1_2, image=image1)
# label.pack(anchor="w")

# frm2_2_2=ttk.Frame(frm2_2, padding=0)
# frm2_2_2.place(height=200, width=600, x=0, y=300)

# ttk.Label(frm2_2_2, text="").grid(column=0, row=0)

# idxs=list(crime_difference.index)
# cols=list(crime_difference.columns)
# for i in range(len(crime_difference.columns)):
#     ttk.Label(frm2_2_2, text=cols[i], font=("Times","12","bold")).grid(column=i+1, row=0, sticky=W)

# for j in range(int(len(idxs)/2)):
#     ttk.Label(frm2_2_2, text=idxs[j], font=("Times","12","bold")).grid(column=0, row=j+1, sticky=W)
#     for i in range(len(cols)):
#         ttk.Label(frm2_2_2, text=str(crime_difference.at[idxs[j],cols[i]]), font=("Times","10")).grid(column=i+1, row=j+1, sticky=W)

# ttk.Label(frm2_2_2, text="").grid(column=4, row=0)
# for i in range(len(crime_difference.columns)):
#     ttk.Label(frm2_2_2, text=cols[i], font=("Times","12","bold")).grid(column=i+5, row=0, sticky=W)
# for j in range(int(len(idxs)/2), len(idxs)):
#     ttk.Label(frm2_2_2, text=idxs[j], font=("Times","12","bold")).grid(column=4, row=j-4, sticky=W)
#     for i in range(len(cols)):
#         ttk.Label(frm2_2_2, text=str(crime_difference.at[idxs[j],cols[i]]), font=("Times","10")).grid(column=i+5, row=j-4, sticky=W)

frm2_1_2=ttk.Frame(frm2_1,padding=10)

CheckVar1=IntVar()
CheckVar2=IntVar()

def check1Changed():
    # cctv
    cctv_data=loadCCTVData('수원시')
    if CheckVar1.get()==1:
        print('cctv checked')
        for i in range(0,len(cctv_data),5):
        # 이거 다 띄우면 화면에 버퍼링생김
        # 일단 5개 마다 한개씩 띄움
            map_widget.set_marker(cctv_data.iloc[i]['위도'], cctv_data.iloc[i]['경도'], text=cctv_data.iloc[i]['설치목적구분'])
    else:
        print('cctv unchecked')

def check2Changed():
    # bell
    emergency_bell_data=loadBellData('수원시')
    if CheckVar2.get()==1:
        print('bell checked')
        for i in range(0,len(emergency_bell_data),5):
        # 이거 다 띄우면 화면에 버퍼링생김
        # 일단 5개 마다 한개씩 띄움
            map_widget.set_marker(emergency_bell_data.iloc[i]['위도'], emergency_bell_data.iloc[i]['경도'])
    else:
        print('bell unchecked')
        
c1=Checkbutton(frm2_1_2,text="CCTV",variable=CheckVar1, command=check1Changed)
c1.grid(column=0, row=0)
c2=Checkbutton(frm2_1_2,text="안전벨",variable=CheckVar2, command=check2Changed)
c2.grid(column=1, row=0)

RadioVariety=IntVar()

def radioChanged():
    
    if RadioVariety.get() == 1:            
        police_data=loadPoliceData('경기도')
        print(police_data)

        print('경찰관 checked')
        colors=["green", "orange", "orangered1","orangered4"]
        for feature in data["features"]:
            city = feature["properties"]["SIG_KOR_NM"]

            for coords in feature["geometry"]["coordinates"]:
                # print(coords)
                for coord in coords:
                    coord[0], coord[1]=coord[1], coord[0]

                # cnt=police_data.loc[(police_data['주소'].str.contains(city))]['증감율']

                for i in range(len(police_data)):
                    if(city in police_data.loc[police_data.index[i],'주소']):
                        cnt=police_data.loc[police_data.index[i],'인원증감']

                
                if cnt<=0:
                    flag=3
                elif cnt<=10:
                    flag=2
                elif cnt<=20:
                    flag=1
                else:
                    flag=0
                    
                polygon_1 = map_widget.set_polygon(coords,
                                    fill_color=colors[flag],
                                    # outline_color="red",
                                    border_width=1,
                                    command=polygon_click,
                                    name=city)

    if RadioVariety.get() == 2:
        print('발생 건수 checked')
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
 

radio1=Radiobutton(frm2_1_2, text="경찰관 수", value=1, variable=RadioVariety, command=radioChanged)
radio1.grid(column=2, row=0)
radio2=Radiobutton(frm2_1_2, text="범죄 발생 건수", value=2, variable=RadioVariety, command=radioChanged)
radio2.grid(column=3, row=0)

frm2_1_2.pack()
frm2_1_2.place(height=50, width=400, x=0, y=470)

      

frm3 = ttk.Frame(root, padding=30)
frm3.place(height=500, width=1150, x=0, y=550)

frm3_1=ttk.Frame(frm3, padding=0)

frm3_1.place(height=500, width=550, x=0, y=0)

image4=PhotoImage(file="FaciDiff.png",master=frm3_1)
label=ttk.Label(frm3_1, image=image4)
label.pack(anchor="w")


frm3_2=ttk.Frame(frm3, padding=0)
frm3_2.place(height=500, width=600, x=550, y=0)

image5=PhotoImage(file="Crime_2017_2018_2.png",master=frm3_1)
label=ttk.Label(frm3_2, image=image5)
label.pack(anchor="w")

current_city = StringVar()
current_city.set('---')

# frm2_2_1=ttk.Frame(frm2_2, padding=0)
# frm2_2_1.place(height=550, width=600, x=0, y=0)

# frm2_2_1_1=ttk.Frame(frm2_2_1, padding=0)
# frm2_2_1_1.place(height=50, width=600, x=0, y=0)
# selected_city_name=ttk.Label(frm2_2_1_1, textvariable=current_city, font=("Times","14","bold"))
# selected_city_name.pack(anchor="nw")

frm5 = ttk.Frame(root, padding=30)
frm5.place(height=500, width=600, x=1150,y=550)
listOfIndex=list(corr_result.index)

flag=False
strAffectable="범죄 감소와 양의 상관관계가 있는 항목은 "
for idx in corr_result.index:
    if(corr_result.loc[idx,'Crime']<0):
        flag=True
        strAffectable=strAffectable+idx+" "

if(flag):
    strAffectable=strAffectable+"입니다"
else:
    strAffectable=strAffectable+"없습니다"


flag=False
strNonAffectable="범죄 감소와 음의 상관관계가 있는 항목은 "
for idx in corr_result.index:
    if(corr_result.loc[idx,'Crime']>0 and corr_result.loc[idx,'Crime']!=1):
        flag=True
        strNonAffectable=strNonAffectable+idx+" "
        
if(flag):
    strNonAffectable=strNonAffectable+"입니다"
else:
    strNonAffectable=strNonAffectable+"없습니다"


ttk.Label(frm5, text="").grid(column=0, row=0)
for i in range(len(listOfIndex)):
    ttk.Label(frm5, text=listOfIndex[i], font=("Times","12","bold")).grid(column=i+1, row=0, sticky=W)

for j in range(len(listOfIndex)):
    ttk.Label(frm5, text=listOfIndex[j], font=("Times","12","bold")).grid(column=0, row=j+1, sticky=W)
    for i in range(len(listOfIndex)):
        ttk.Label(frm5, text=str(corr_result.at[listOfIndex[j],listOfIndex[i]]), font=("Times","12")).grid(column=i+1, row=j+1, sticky=W)

ttk.Label(frm5, text="", font=("Times","14")).grid(column=0, row=5, columnspan=5, sticky=W)
ttk.Label(frm5, text=strAffectable, font=("Times","12")).grid(column=0, row=6, columnspan=5, sticky=W)
ttk.Label(frm5, text=strNonAffectable, font=("Times","12")).grid(column=0, row=7, columnspan=5, sticky=W)


root.mainloop()
