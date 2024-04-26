import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#df = pd.read_csv("processed/240407/evening/data199.csv")
df = pd.read_csv("processed/240426/data127.csv")
#df = pd.read_csv("processed/240426/data127.csv")

"""plt.title("processed/240426/data127.csv\nDrake Practice")
plt.plot(df["time (s)"], df["fl wheel ambient temp (C)"], c='r', label="FL Ambient")
plt.plot(df["time (s)"], df["fl rotor temp (C)"], c='b', label="FL Rotor")

plt.plot(df["time (s)"], df["fr wheel ambient temp (C)"], c='g', label="FR Ambient")
plt.plot(df["time (s)"], df["fr rotor temp (C)"], c='orange', label="FR Rotor")
plt.xlabel("Time (s)")
plt.ylabel("Temperature (C)")
plt.legend()
plt.show()

plt.clf()"""

plt.plot(df["time (s)"], df["fr wheel speed (rpm)"], label="FR")
plt.plot(df["time (s)"], df["fl wheel speed (rpm)"], label="FL")
plt.plot(df["time (s)"], df['gps speed (m/s)'], label="GPS")
plt.legend()
plt.show()

"""plt.clf()

fdf = df.loc[df["time (s)"] > 700]
diff = np.abs(fdf["fr wheel speed (rpm)"] - fdf["fl wheel speed (rpm)"])
print(
diff.describe()
)
#plt.plot(fdf["time (s)"], diff)
plt.boxplot(diff)
plt.show()"""