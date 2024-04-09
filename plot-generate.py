import matplotlib.pyplot as plt
import pandas as pd

def generate_report(path: str, session: str, day: str, runno: str):
    df = pd.read_csv(path)
    figure, axis = plt.subplots(2, 3)
    figure.suptitle("File: " + path)
    figure.set_size_inches(16, 9)

    # G-G diagram
    axis[0, 0].grid(visible=True)
    axis[0, 0].set_xlim(-1200, 1200)
    axis[0, 0].set_ylim(-1200, 1200)
    axis[0, 0].set_xlabel("Lateral Acceleration (mG)")
    axis[0, 0].set_ylabel("Longitudinal Acceleration (mG)")
    axis[0, 0].scatter(df["lateral accel (mG)"], df["longitudinal accel (mG)"], s=5)
    axis[0, 0].set_title("G-G Diagram")

    # Braking vs Rear Brake Pressure
    axis[1, 0].set_ylim(-1200, 100)
    axis[1, 0].set_xlabel("Rear Brake Pressure (bar)")
    axis[1, 0].set_ylabel("Longitudinal Acceleration (mG)")
    axis[1, 0].scatter(df["r brake pressure (bar)"], df["longitudinal accel (mG)"], s=5)
    axis[1, 0].set_title("Rear Brake Pressure")

    # IMU vs Time
    axis[0, 1].set_title("IMU vs Time")
    axis[0, 1].set_xlabel("Time (s)")
    axis[0, 1].set_ylabel("Acceleration (mG)")
    axis[0, 1].plot(df["time (s)"], df["longitudinal accel (mG)"], label="longitudinal")
    axis[0, 1].plot(df["time (s)"], df["lateral accel (mG)"], label="lateral")
    axis[0, 1].legend()

    # Rotor Temperature vs Time
    # skipped if we dont have data
    if df["fl rotor temp (C)"].max() > -270 or df["fr rotor temp (C)"].max() > -270:
        axis[0, 2].set_title("Rotor Temperature vs Time")
        axis[0, 2].set_xlabel("Time (s)")
        axis[0, 2].set_ylabel("Temperature (C)")
        axis[0, 2].plot(df["time (s)"], df["fl rotor temp (C)"], label="FL Rotor")
        axis[0, 2].plot(df["time (s)"], df["fr rotor temp (C)"], label="FR Rotor")
        axis[0, 2].legend()

    # Shock Displacement vs Time
    flsz = df["fl shock position (mm)"].head(1000).median()
    frsz = df[" fr shock position (mm)"].head(1000).median()
    rrsz = df["rr shock position (mm)"].head(1000).median()
    rlsz = df["rl shock position (mm)"].head(1000).median()
    df["fl displacement"] = df["fl shock position (mm)"] - flsz
    df["fr displacement"] = df[" fr shock position (mm)"] - frsz
    df["rr displacement"] = df["rr shock position (mm)"] - rrsz
    df["rl displacement"] = df["rl shock position (mm)"] - rlsz
    axis[1, 1].set_title("Shock Displacement")
    axis[1, 1].set_xlabel("Time (s)")
    axis[1, 1].set_ylabel("Displacement (mm)")
    axis[1, 1].plot(df["time (s)"], df["fl displacement"], label="FL")
    axis[1, 1].plot(df["time (s)"], df["fr displacement"], label="FR")
    axis[1, 1].plot(df["time (s)"], df["rr displacement"], label="RR")
    axis[1, 1].plot(df["time (s)"], df["rl displacement"], label="RL")
    axis[1, 1].legend()
    

    plt.savefig("reports/" + day + "/" + session + "/plots" + runno + ".png")


# evening
print("evening")
for i in range(180, 200):
    generate_report("processed/240407/evening/data" + str(i) + ".csv", "evening", "240407", str(i))

# shakedown
print("shakedown")
for i in range(136, 160):
    generate_report("processed/240407/shakedown/data" + str(i) + ".csv", "shakedown", "240407", str(i))

# matt autox
print("matt")
for i in range(163, 180):
    if i == 164:
        continue
    generate_report("processed/240407/matt-et-al/data" + str(i) + ".csv", "matt-et-al", "240407", str(i))