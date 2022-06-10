import pandas as pd
import matplotlib.pyplot as plt

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

temp=crime_2017
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

print(x)
print(summations)

plt.barh(range(len(x)), summations)
plt.title('Total crime counts by city', fontsize=18)
plt.ylabel('City', fontsize=15)
plt.xlabel('Crime counts', fontsize=15)
plt.yticks(range(len(x)), x, fontsize=13, rotation=0)
plt.show()

# plt.stackplot(x,y_list,labels = ['강력', '절도', '폭력', '지능', '풍속', '특별경제', '마약', '보건', '환경', '교통'])
# plt.legend(loc='upper left')
# plt.title('ratio of crime for every cities in 2017')
# plt.show()
