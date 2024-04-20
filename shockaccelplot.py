import matplotlib.pyplot as plt
import pandas as pd

def meow(path, day, event, runno):
    df = pd.read_csv(path)
    print(path)

    fig, ax = plt.subplots()

    plt.suptitle("File: " + path + "\nright shocks and longitudinal acceleration\n240419")
    ax.set_xlabel("longitudinal acceleration (mG)")
    ax.set_ylabel("shock displacement (mm)")

    # "fr shock velocity (mm/s)"
    # "fr displacement (mm)"
    plt.scatter(df["longitudinal accel (mG)"], df["fr displacement (mm)"], s=2, c='r', label="FR")
    plt.scatter(df["longitudinal accel (mG)"], df["rr displacement (mm)"], s=2, c='b', label="RR")
    plt.legend()

    plt.savefig("reports/240419/rightshocks-" + event + runno + ".png")


for i in range(64, 67):
    meow("processed/everything/data" + str(i) + ".csv", "240419", "shakedown", str(i))

meow("processed/everything/data69.csv", "240419", "accel", str(69))
meow("processed/everything/data72.csv", "240419", "aero-coastdown", str(72))
meow("processed/everything/data73.csv", "240419", "aero-coastdown", str(73))