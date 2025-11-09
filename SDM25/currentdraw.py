import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("processed/everything/data69.csv")

fig, ax = plt.subplots()
plt.suptitle("current draw\nprocessed/everything/data69.csv\naccel 240419")

plt.plot(df["time (s)"], df["current draw (mA)"])
plt.legend()
ax.set_xlabel("time (s)")
ax.set_ylabel("current draw (mA)")

"""ax2 = ax.twinx()
ax2.set_ylabel("battery voltage (V)")
ax2.plot(df["time (s)"], df["battery (V)"], 'r')"""
plt.show()