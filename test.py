import pandas as pd
import matplotlib.pyplot as plt

womenMeans = (25, 32, 34, 20, -25)
plt.bar(range(len(womenMeans)),womenMeans)
plt.show()