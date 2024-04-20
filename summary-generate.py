import pandas as pd

def generate_summary(path: str, session: str, day: str):
    df = pd.read_csv(path)
    print("generating summary for " + path + ":")
    print("length of file (s): ", end="")
    print(df["time (s)"].max())

    print("peak accel (mG): ", end="")
    print(df["longitudinal accel (mG)"].max())

    print("peak braking (mG): ", end="")
    print(df["longitudinal accel (mG)"].min())

    print("peak cornering (mG): ", end="")
    print(max(df["lateral accel (mG)"].max(), abs(df["lateral accel (mG)"].min())))

    print("max FL wheel RPM: ", end="")
    print(df["fl wheel speed (rpm)"].max())

    print("max FL rotor temperature (C): ", end="")
    print(df["fl rotor temp (C)"].max())

    print("max FR wheel RPM: ", end="")
    print(df["fr wheel speed (rpm)"].max())

    print("max FR rotor temperature (C): ", end="")
    print(df["fr rotor temp (C)"].max())

    print("FR shock travel range (mm): ", end="")
    print(df["fr shock position (mm)"].max() - df["fr shock position (mm)"].min())

    print("FL shock travel range (mm): ", end="")
    print(df["fl shock position (mm)"].max() - df["fl shock position (mm)"].min())

    print("RL shock travel range (mm): ", end="")
    print(df["rl shock position (mm)"].max() - df["rl shock position (mm)"].min())

    print("RR shock travel range (mm): ", end="")
    print(df["rr shock position (mm)"].max() - df["rr shock position (mm)"].min())

    print("steering right:", end="")
    print(df["steering (degrees)"].max())

    print("steering left:", end="")
    print(df["steering (degrees)"].min())

    print("# of tests: ", end="")
    print(df["test number"].max())
    print("")
    return df["time (s)"].max(), df["longitudinal accel (mG)"].max()



longruns = []
inertial = []
print("shakedown summaries")
for i in range(60, 75):
    length, accel = generate_summary("processed/everything/data" + str(i) + ".csv", "evening", "240407")
    if length > 120:
        longruns.append(i)
    if accel > 100:
        inertial.append(i)

print("runs longer than 120 seconds: ", end="")
print(longruns)

print("runs with > 100mG of accel: ", end="")
print(inertial)

