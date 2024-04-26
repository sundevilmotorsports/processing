import pandas as pd
import matplotlib.pyplot as plt

#df = pd.read_csv("processed/240407/evening/data199.csv")
df = pd.read_csv("processed/coastdown-240418/data48.csv")

print(df["fl wheel ambient temp (C)"].describe())
print(df["fr wheel ambient temp (C)"].describe())
print(df["fr rotor temp (C)"].describe())

plt.plot(df["time (s)"], df["fl wheel ambient temp (C)"], c='r')
plt.plot(df["time (s)"], df["fl rotor temp (C)"], c='b')

plt.plot(df["time (s)"], df["fr wheel ambient temp (C)"], c='g')
plt.plot(df["time (s)"], df["fr rotor temp (C)"], c='orange')
plt.show()