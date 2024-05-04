import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#df = pd.read_csv("processed/240407/evening/data199.csv")
df = pd.read_csv("processed/240428/data34.csv")
#df = pd.read_csv("processed/240426/data127.csv")

plt.title("processed/240428/data34.csv")
fig, ax = plt.subplots()
#ax2 = ax.twinx()
ax.plot(df["time (s)"], df["fl wheel ambient temp (C)"], label="FL Ambient")
ax.plot(df["time (s)"], df["fl rotor temp (C)"], label="FL Rotor")

ax.plot(df["time (s)"], df["fr wheel ambient temp (C)"], label="FR Ambient")
ax.plot(df["time (s)"], df["fr rotor temp (C)"], label="FR Rotor")

ax.plot(df["time (s)"], df["rl wheel ambient temp (C)"], label="RL Ambient")
ax.plot(df["time (s)"], df["rl rotor temp (C)"], label="RL Rotor")
ax.plot(df["time (s)"], df["brake fluid temp (C)"], label="Brake Fluid")

"""ax.plot(df["time (s)"], df["fr displacement (mm)"], label="FR")
ax.plot(df["time (s)"], df["fl displacement (mm)"], label="FL")
ax.plot(df["time (s)"], df["rl displacement (mm)"], label="RL")
ax.plot(df["time (s)"], df["rr displacement (mm)"], label="RR")"""

ax.set_xlabel("Time (s)")
ax.set_ylabel("Temperature (C)")
fig.legend()
plt.show()

plt.clf()
"""
plt.plot(df["time (s)"], df["fr wheel speed (rpm)"], label="FR")
plt.plot(df["time (s)"], df["fl wheel speed (rpm)"], label="FL")
plt.plot(df["time (s)"], df['gps speed (m/s)'], label="GPS")
plt.legend()
plt.show()"""

"""plt.clf()

fdf = df.loc[df["time (s)"] > 700]
diff = np.abs(fdf["fr wheel speed (rpm)"] - fdf["fl wheel speed (rpm)"])
print(
diff.describe()
)
#plt.plot(fdf["time (s)"], diff)
plt.boxplot(diff)
plt.show()"""