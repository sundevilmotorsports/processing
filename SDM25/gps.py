import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("processed/240426/data123.csv")

gps = df.loc[df["gps fix"] == 3]

plt.plot(gps["gps longitude"], gps["gps latitude"])
plt.show()