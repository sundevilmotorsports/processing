import pandas as pd

def owo(path):
    print(path)
    df = pd.read_csv(path)
    flsz = df["fl shock position (mm)"].head(1000).median()
    frsz = df["fr shock position (mm)"].head(1000).median()
    rrsz = df["rr shock position (mm)"].head(1000).median()
    rlsz = df["rl shock position (mm)"].head(1000).median()
    df["fl displacement (mm)"] = df["fl shock position (mm)"] - flsz
    df["fr displacement (mm)"] = df["fr shock position (mm)"] - frsz
    df["rr displacement (mm)"] = df["rr shock position (mm)"] - rrsz
    df["rl displacement (mm)"] = df["rl shock position (mm)"] - rlsz
    df.loc[0, "fl displacement (mm)"] = 0.0
    df.loc[0, "fr displacement (mm)"] = 0.0
    df.loc[0, "rr displacement (mm)"] = 0.0
    df.loc[0, "rl displacement (mm)"] = 0.0

    df.loc[0, "steering (degrees)"] = 0.0


    df["time delta (s)"] = df["time (s)"].diff()
    df.loc[0, "time delta (s)"] = 0.0

    df["fl shock velocity (mm/s)"] = df["fl displacement (mm)"].diff().fillna(0.0) / df["time delta (s)"]
    df["fr shock velocity (mm/s)"] = df["fr displacement (mm)"].diff().fillna(0.0) / df["time delta (s)"]
    df["rr shock velocity (mm/s)"] = df["rr displacement (mm)"].diff().fillna(0.0) / df["time delta (s)"]
    df["rl shock velocity (mm/s)"] = df["rl displacement (mm)"].diff().fillna(0.0) / df["time delta (s)"]

    print("oh no")
    df["fl shock velocity (mm/s)"] = df["fl shock velocity (mm/s)"].fillna(0.0)
    df["fr shock velocity (mm/s)"] = df["fr shock velocity (mm/s)"].fillna(0.0)
    df["rr shock velocity (mm/s)"] = df["rr shock velocity (mm/s)"].fillna(0.0)
    df["rl shock velocity (mm/s)"] = df["rl shock velocity (mm/s)"].fillna(0.0)
    df.to_csv(path)


for i in range(60, 75):
    owo("processed/everything/data" +str(i) +".csv")