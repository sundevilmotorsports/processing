import matplotlib.pyplot as plt
import pandas as pd

def latplot(path, event, runno):
    df = pd.read_csv(path)
    print(path)

    front_df = df.loc[(df["lateral accel (mG)"] <= 1500) & (df["lateral accel (mG)"] >= 0)].copy()
    rear_df = front_df.copy()
    front_df["fronts"] = front_df["fr shock velocity (mm/s)"]
    front_df["fronts"] += front_df["fl shock velocity (mm/s)"]
    rear_df["rears"] = rear_df["rr shock velocity (mm/s)"]
    rear_df["rears"] += rear_df["rl shock velocity (mm/s)"]
    

    front_df = front_df.loc[(front_df["fronts"] >= -350) & (front_df["fronts"] <= 350)]
    rear_df = rear_df.loc[(rear_df["rears"] <= 350) & (rear_df["rears"] >= -350)]


    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.canvas.manager.full_screen_toggle()
    fig.suptitle("File: " + path + "\nfront and rear shock load vs lateral acceleration")
    
    ax1.plot(0)
    ax1.set_xlabel("lateral acceleration (mG)")
    ax1.set_ylabel("shock velocity(mm/s)")
    ax1.set_xlim(0, 1500)
    ax1.set_ylim(-350, 350)
    ax1.set_title("Fronts")
    
    ax2.plot(1)
    ax2.set_xlabel("lateral acceleration (mG)")
    ax2.set_xlim(0, 1500)
    ax2.set_ylim(-350, 350)
    ax2.set_title("Rears")

    ax1.scatter(front_df["lateral accel (mG)"], front_df["fronts"], s=2, c = 'r', label="Fronts", alpha=0.5)
    ax2.scatter(rear_df["lateral accel (mG)"], rear_df["rears"], s=2,c = 'b', label="Rears", alpha=0.5)
    plt.savefig("reports/everything/" + runno + "front-rear-load-vs-latitude" + event + ".png")
    plt.show()
    

def longplot(path, event, runno):
    df = pd.read_csv(path)
    print(path)

    breaking_df = df.loc[df["longitudinal accel (mG)"] <= 0][["longitudinal accel (mG)","fl shock velocity (mm/s)", "fr shock velocity (mm/s)"]].copy()
    accel_df = df.loc[df["longitudinal accel (mG)"] >= 0][["longitudinal accel (mG)","fl shock velocity (mm/s)", "fr shock velocity (mm/s)"]].copy()
    breaking_df["load"] = breaking_df.loc[breaking_df["fl shock velocity (mm/s)"] <= 0]["fl shock velocity (mm/s)"]
    breaking_df["load"] += breaking_df.loc[breaking_df["fr shock velocity (mm/s)"] <= 0]["fr shock velocity (mm/s)"]

    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.canvas.manager.full_screen_toggle()
    fig.suptitle("File: " + path + "\nlongitudinal acceleration vs shock velocity")
    ax1.plot(0)
    ax1.set_xlabel("longitudinal acceleration (mG)")
    ax1.set_ylabel("shock velocity (mm/s)")
    ax1.set_xlim(-1000, 0)
    ax1.set_ylim(-250, 0)
    ax1.set_title("Braking")
    
    ax2.plot(1)
    ax2.set_xlabel("longitudinal acceleration (mG)")
    ax2.set_xlim(0, 1000)
    ax2.set_ylim(-250, 0)
    ax2.set_title("Accelerating")

    ax1.scatter(breaking_df["longitudinal accel (mG)"], breaking_df["fl shock velocity (mm/s)"], s=2, c = 'red',label="front left", alpha=0.5)
    ax1.scatter(breaking_df["longitudinal accel (mG)"], breaking_df["fr shock velocity (mm/s)"], s=2, c = 'black',label="front right", alpha=0.5)
    ax2.scatter(accel_df["longitudinal accel (mG)"], accel_df["fl shock velocity (mm/s)"], s=2, c = 'red',label="front left", alpha=0.5)
    ax2.scatter(accel_df["longitudinal accel (mG)"], accel_df["fr shock velocity (mm/s)"], s=2, c = 'black',label="front right", alpha=0.5)

    ax1.legend()
    ax2.legend()
    plt.savefig("reports/everything/" + runno + "longitudinal-vs-load" + event + ".png")
    plt.show()

def combined(path, event, runno):
    df = pd.read_csv(path)
    print(path)

    front_df = df.loc[(df["lateral accel (mG)"] <= 1500) & (df["lateral accel (mG)"] >= -2000)][["lateral accel (mG)","fr shock velocity (mm/s)","fl shock velocity (mm/s)", "rr shock velocity (mm/s)", "rl shock velocity (mm/s)"]].copy()
    rear_df = front_df.copy()
    front_df["avg_fronts"] = (front_df["fr shock velocity (mm/s)"] + front_df["fl shock velocity (mm/s)"])/2
    rear_df["avg_rears"] = (rear_df["rr shock velocity (mm/s)"] + rear_df["rl shock velocity (mm/s)"])/2

    accel_df = front_df.loc[front_df["avg_fronts"] >= 0].copy()    
    accel_df["avg_rear"] = rear_df.loc[rear_df["avg_rears"] <= 0]["avg_rears"].copy()

    deccel_df = front_df.loc[front_df["avg_fronts"] <= 0].copy()    
    deccel_df["avg_rear"] = rear_df.loc[rear_df["avg_rears"] >= 0]["avg_rears"].copy()
    
    fig, (ax1, ax2) = plt.subplots(2)
    fig.canvas.manager.full_screen_toggle()
    fig.suptitle("File: " + path + "\nlongitudinal acceleration vs avg fronts and rear velocity")

    ax1.plot(0)
    ax1.set_ylabel("average velocity(mm/s)")
    ax1.set_xlim(-350, 1300)
    ax1.set_ylim(-150, 500)
    ax1.set_title("Accelerating")
    
    ax2.plot(1)
    ax2.set_xlabel("average velocity(mm/s)")
    ax2.set_ylabel("shock velocity (mm/s)")
    ax2.set_xlim(-350, 1300)
    ax2.set_ylim(-450, 150)
    ax2.set_title("Decelerating")

    ax1.scatter(deccel_df["lateral accel (mG)"], deccel_df["avg_fronts"], s=2, c='r', label = "average front value", alpha=0.5)
    ax1.scatter(deccel_df["lateral accel (mG)"], deccel_df["avg_rear"], s=2, c='b', label = "average rear value", alpha=0.5)
    ax2.scatter(accel_df["lateral accel (mG)"], accel_df["avg_fronts"], s=1, c = 'r', label = "average front value",alpha = 0.5)
    ax2.scatter(accel_df["lateral accel (mG)"], accel_df["avg_rear"], s=2, c = 'b', label = "average rear value",alpha = 0.5)

    ax1.legend()
    ax2.legend()
    plt.savefig("reports/everything/" + runno + "longitudinal-vs-avg" + event + ".png")
    plt.show()

latplot("processed/everything/data69.csv", "data", "69")
longplot("processed/everything/data69.csv", "data", "69")
combined("processed/everything/data69.csv", "data", "69")
"""
# shakedown
for i in range(64, 67):
    longplot("processed/everything/data" + str(i) + ".csv", "shakedown", str(i))
    latplot("processed/everything/data" + str(i) + ".csv", "shakedown", str(i))

# coastdown aero
for i in range(72, 74):
    longplot("processed/everything/data" + str(i) + ".csv", "coastdown-aero", str(i))
    latplot("processed/everything/data" + str(i) + ".csv", "coastdown-aero", str(i))
"""