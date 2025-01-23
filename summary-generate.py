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

    print("max RR wheel RPM: ", end="")
    print(df["rr wheel speed (rpm)"].max())

    print("max RR rotor temperature (C): ", end="")
    print(df["rr rotor temp (C)"].max())

    print("max RL wheel RPM: ", end="")
    print(df["rl wheel speed (rpm)"].max())

    print("max RL rotor temperature (C): ", end="")
    print(df["rl rotor temp (C)"].max())

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

    print("current draw (mA): ", end="")
    print(df["current draw (mA)"].describe())

    print("GPS fix acquired at: ", end="")
    gps = df[df["gps fix"] == 3]
    if gps.shape[0] > 0:
        gps_time = df[df["gps fix"] == 3].iloc[0]["time (s)"]
    else:
        gps_time = 0
    print(gps_time, end=" seconds\n")
    print(df["gps speed (m/s)"].describe())
    print("")

    return df["time (s)"].max(), df["longitudinal accel (mG)"].max(), gps_time, df["fl wheel speed (rpm)"].max()



longruns = []
inertial = []
gps = []
wheel = []

print("241103 summaries")
for i in range(97, 98):
    length, accel, fixtime, rpm = generate_summary("processed/241103/data" + str(i) + ".csv", "", "")
    if length > 120:
        longruns.append(i)
    if accel > 100:
        inertial.append(i)
    if fixtime > 0:
        gps.append(i)
    if rpm > 5:
        wheel.append(i)


print("runs longer than 120 seconds: ", end="")
print(longruns)

print("runs with > 100mG of accel: ", end="")
print(inertial)

print("runs with gps: ", end="")
print(gps)

print("runs with nonzero wheelspeed: ", end ="")
print(wheel)
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

print("feasible runs: ", end="")
print(intersection(wheel, intersection(longruns, inertial)))
