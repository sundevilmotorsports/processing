import matplotlib.pyplot as plt
import pandas as pd

def generate_report(path: str, session: str, day: str, runno: str):
    df = pd.read_csv(path)
    figure, axis = plt.subplots(2, 3)
    figure.suptitle("File: " + path)
    figure.set_size_inches(16, 9)

    # G-G diagram
    axis[0, 0].grid(visible=True)
    axis[0, 0].set_xlim(-1600, 1600)
    axis[0, 0].set_ylim(-1600, 1600)
    axis[0, 0].set_xlabel("Lateral Acceleration (mG)")
    axis[0, 0].set_ylabel("Longitudinal Acceleration (mG)")
    axis[0, 0].scatter(df["lateral accel (mG)"], df["longitudinal accel (mG)"], s=1)
    axis[0, 0].set_title("G-G Diagram")

    # Braking vs Rear Brake Pressure
    axis[1, 0].set_ylim(-1200, 100)
    axis[1, 0].set_xlabel("Rear Brake Pressure (bar)")
    axis[1, 0].set_ylabel("Longitudinal Acceleration (mG)")
    axis[1, 0].scatter(df["r brake pressure (bar)"], df["longitudinal accel (mG)"], s=1)
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
    axis[1, 1].set_title("Shock Displacement")
    axis[1, 1].set_xlabel("Time (s)")
    axis[1, 1].set_ylabel("Displacement (mm)")
    #axis[1, 1].plot(df["time (s)"], df["fl displacement (mm)"], label="FL")
    #axis[1, 1].plot(df["time (s)"], df["fr displacement (mm)"], label="FR")
    #axis[1, 1].plot(df["time (s)"], df["rr displacement (mm)"], label="RR")
    #axis[1, 1].plot(df["time (s)"], df["rl displacement (mm)"], label="RL")
    axis[1, 1].legend()

    # wheel RPM vs Time
    axis[1, 2].set_title("wheel RPM")
    axis[1, 2].set_xlabel("Time (s)")
    axis[1, 2].set_ylabel("Wheel Speed (RPM)")
    axis[1, 2].plot(df["time (s)"], df["fl wheel speed (rpm)"], label="FL")
    axis[1, 2].plot(df["time (s)"], df["fr wheel speed (rpm)"], label="FR")

    ax2 = axis[1,2].twinx()
    ax2.set_ylabel("test number", color="tab:red")
    ax2.plot(df["time (s)"], df["test number"], 'r')

    axis[1, 2].legend()
    #plt.show()
    plt.savefig("reports/" + day + "/" + session + "/plots" + runno + ".png")


"""print("shakedown")
for i in range(64, 67):
    generate_report("processed/everything/data" + str(i) + ".csv", "accel", "240419", str(i))
"""

#generate_report("processed/240426/data127.csv", "ff", "aa", 69)
for i in range(115, 128):
    generate_report("processed/240426/data" + str(i) + ".csv", "hehe", "240426", str(i))