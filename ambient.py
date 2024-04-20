import pandas as pd

df = pd.read_csv("processed/everything/data66.csv")

print(df["fl wheel ambient temp (C)"].describe())
print(df["fr wheel ambient temp (C)"].describe())
print(df["fr rotor temp (C)"].describe())