import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

year2017=[672,5494,7919,7973,595,1133,158,318,32,14266]
year2018=[637,5381,8071,8723,613,1131,98,355,35,11159]

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
    rects = plt.barh(['2017','2018'], widths, left=starts, height=0.5,
                    label=category_names[i])

plt.legend(loc="lower left", ncol=len(category_names)//2)
plt.show()