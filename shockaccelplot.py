import matplotlib.pyplot as plt
import pandas as pd

def latplot(path, event, runno):
    df = pd.read_csv(path)
    print(path)

    fig, ax = plt.subplots()
    fig.suptitle("File: " + path + "; 240419\nshaft velocity vs lateral acceleration\n2 turns highspeed compression")
    
    ax.set_xlabel("lateral acceleration (mG)")
    ax.set_ylabel("shock velocity (mm/s)")

    flt_df = df.loc[(df["longitudinal accel (mG)"] <= 250) & (df["longitudinal accel (mG)"] >= -250)]

    ax.scatter(flt_df["lateral accel (mG)"], flt_df["rl shock velocity (mm/s)"], s=1, label="RL", alpha=0.5)
    ax.scatter(flt_df["lateral accel (mG)"], flt_df["rr shock velocity (mm/s)"], s=1, label="RR", alpha=0.5)
    ax.scatter(flt_df["lateral accel (mG)"], flt_df["fr shock velocity (mm/s)"], s=1, label="FR", alpha=0.5)
    ax.scatter(flt_df["lateral accel (mG)"], flt_df["fl shock velocity (mm/s)"], s=1, label="FL", alpha=0.5)
    ax.legend()
    plt.savefig("reports/240419/vel/" + runno + "-shocks-lateral-" + event + ".png")

    plt.clf()
    fig, ax = plt.subplots()
    fig.suptitle("File: " + path + "; 240419\nFL shaft velocity vs lateral acceleration\n2 turns highspeed compression")
    ax.set_xlabel("lateral acceleration (mG)")
    ax.set_ylabel("shock velocity (mm/s)")
    ax.scatter(flt_df["lateral accel (mG)"], flt_df["fl shock velocity (mm/s)"], s=1)
    plt.savefig("reports/240419/vel/" + runno + "-FL-shocks-lateral-" + event + ".png")

    plt.clf()
    fig, ax = plt.subplots()
    fig.suptitle("File: " + path + "; 240419\nFR shaft velocity vs lateral acceleration\n2 turns highspeed compression")
    ax.set_xlabel("lateral acceleration (mG)")
    ax.set_ylabel("shock velocity (mm/s)")
    ax.scatter(flt_df["lateral accel (mG)"], flt_df["fr shock velocity (mm/s)"], s=1)
    plt.savefig("reports/240419/vel/" + runno + "-FR-shocks-lateral-" + event + ".png")

    plt.clf()
    fig, ax = plt.subplots()
    fig.suptitle("File: " + path + "; 240419\nRR shaft velocity vs lateral acceleration\n2 turns highspeed compression")
    ax.set_xlabel("lateral acceleration (mG)")
    ax.set_ylabel("shock velocity (mm/s)")
    ax.scatter(flt_df["lateral accel (mG)"], flt_df["rr shock velocity (mm/s)"], s=1)
    plt.savefig("reports/240419/vel/" + runno + "-RR-shocks-lateral-" + event + ".png")

    plt.clf()
    fig, ax = plt.subplots()
    fig.suptitle("File: " + path + "; 240419\nRL shaft velocity vs lateral acceleration\n2 turns highspeed compression")
    ax.set_xlabel("lateral acceleration (mG)")
    ax.set_ylabel("shock velocity (mm/s)")
    ax.scatter(flt_df["lateral accel (mG)"], flt_df["rl shock velocity (mm/s)"], s=1)
    plt.savefig("reports/240419/vel/" + runno + "-RL-shocks-lateral-" + event + ".png")

def longplot(path, event, runno):
    df = pd.read_csv(path)
    print(path)

    fig, ax = plt.subplots()
    fig.suptitle("File: " + path + "; 240419\nshaft velocity vs longitudinal acceleration\n2 turns highspeed compression")
    
    ax.set_xlabel("longitudinal acceleration (mG)")
    ax.set_ylabel("shock velocity (mm/s)")

    flt_df = df.loc[(df["lateral accel (mG)"] <= 250) & (df["lateral accel (mG)"] >= -250)]

    ax.scatter(flt_df["longitudinal accel (mG)"], flt_df["rl shock velocity (mm/s)"], s=1, label="RL", alpha=0.5)
    ax.scatter(flt_df["longitudinal accel (mG)"], flt_df["rr shock velocity (mm/s)"], s=1, label="RR", alpha=0.5)
    ax.scatter(flt_df["longitudinal accel (mG)"], flt_df["fr shock velocity (mm/s)"], s=1, label="FR", alpha=0.5)
    ax.scatter(flt_df["longitudinal accel (mG)"], flt_df["fl shock velocity (mm/s)"], s=1, label="FL", alpha=0.5)
    ax.legend()
    plt.savefig("reports/240419/vel/" + runno + "-shocks-longitudinal-" + event + ".png")

    plt.clf()
    fig, ax = plt.subplots()
    fig.suptitle("File: " + path + "; 240419\nFL shaft velocity vs longitudinal acceleration\n2 turns highspeed compression")
    ax.set_xlabel("longitudinal acceleration (mG)")
    ax.set_ylabel("shock velocity (mm/s)")
    ax.scatter(flt_df["longitudinal accel (mG)"], flt_df["fl shock velocity (mm/s)"], s=1)
    plt.savefig("reports/240419/vel/" + runno + "-FL-shocks-longitudinal-" + event + ".png")

    plt.clf()
    fig, ax = plt.subplots()
    fig.suptitle("File: " + path + "; 240419\nFR shaft velocity vs longitudinal acceleration\n2 turns highspeed compression")
    ax.set_xlabel("longitudinal acceleration (mG)")
    ax.set_ylabel("shock velocity (mm/s)")
    ax.scatter(flt_df["longitudinal accel (mG)"], flt_df["fr shock velocity (mm/s)"], s=1)
    plt.savefig("reports/240419/vel/" + runno + "-FR-shocks-longitudinal-" + event + ".png")

    plt.clf()
    fig, ax = plt.subplots()
    fig.suptitle("File: " + path + "; 240419\nRR shaft velocity vs longitudinal acceleration\n2 turns highspeed compression")
    ax.set_xlabel("longitudinal acceleration (mG)")
    ax.set_ylabel("shock velocity (mm/s)")
    ax.scatter(flt_df["longitudinal accel (mG)"], flt_df["rr shock velocity (mm/s)"], s=1)
    plt.savefig("reports/240419/vel/" + runno + "-RR-shocks-longitudinal-" + event + ".png")

    plt.clf()
    fig, ax = plt.subplots()
    fig.suptitle("File: " + path + "; 240419\nRL shaft velocity vs longitudinal acceleration\n2 turns highspeed compression")
    ax.set_xlabel("longitudinal acceleration (mG)")
    ax.set_ylabel("shock velocity (mm/s)")
    ax.scatter(flt_df["longitudinal accel (mG)"], flt_df["rl shock velocity (mm/s)"], s=1)
    plt.savefig("reports/240419/vel/" + runno + "-RL-shocks-longitudinal-" + event + ".png")

# accel
longplot("processed/everything/data69.csv", "accel", "69")
latplot("processed/everything/data69.csv", "accel", "69")

# shakedown
for i in range(64, 67):
    longplot("processed/everything/data" + str(i) + ".csv", "shakedown", str(i))
    latplot("processed/everything/data" + str(i) + ".csv", "shakedown", str(i))

# coastdown aero
for i in range(72, 74):
    longplot("processed/everything/data" + str(i) + ".csv", "coastdown-aero", str(i))
    latplot("processed/everything/data" + str(i) + ".csv", "coastdown-aero", str(i))