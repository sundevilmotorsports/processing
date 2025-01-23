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
        axis[0, 2].plot(df["time (s)"], df["rr rotor temp (C)"], label="RR Rotor")
        axis[0, 2].plot(df["time (s)"], df["rl rotor temp (C)"], label="RL Rotor")
        axis[0, 2].legend()

    # GPS
    axis[1, 1].set_title("GPS")
    axis[1, 1].set_xlabel("longitude")
    axis[1, 1].set_ylabel("latitude")
    gps = df.loc[df["gps fix"] == 3]
    if runno == "38":
        gps = gps.loc[gps["gps longitude"] > 300]
    axis[1, 1].plot(gps["gps longitude"], gps["gps latitude"])

    # wheel RPM vs Time
    axis[1, 2].set_title("wheel RPM")
    axis[1, 2].set_xlabel("Time (s)")
    axis[1, 2].set_ylabel("Wheel Speed (RPM)")
    axis[1, 2].plot(df["time (s)"], df["fl wheel speed (rpm)"], label="FL")
    axis[1, 2].plot(df["time (s)"], df["rr wheel speed (rpm)"], label="RR")
    axis[1, 2].plot(df["time (s)"], df["rl wheel speed (rpm)"], label="RL")

    ax2 = axis[1,2].twinx()
    ax2.set_ylabel("test number", color="tab:red")
    ax2.plot(df["time (s)"], df["test number"], 'r')

    axis[1, 2].legend()
    #plt.show()
    plt.savefig("processed/" + day + "/" + session + "/plots" + runno + ".png")


#generate_report("processed/240921/data" + "50" + ".csv", "auto", "240921", str(50))
#hehe = [3, 19, 21, 22, 23, 24, 30, 32, 34, 35, 37, 38, 200, 204, 206, 207, 208, 209, 210, 211, 212, 213, 215]
for i in range(65,75):
    pass
    generate_report("processed/241103/data" + str(i) + ".csv", "auto", "241103", str(i))

