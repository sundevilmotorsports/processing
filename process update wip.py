# commit hash 20321ad 240424
from transfer import linearPotentiometer, brakePressure, mlx90614, steering, fr_sg, fl_sg, rl_sg
from sus import owo as shock_vel
from pathlib import Path
import os
import csv
# cwd = os.getcwd()
# print(cwd)

def parseBenjiFile(number: int, path: str, session: str):
    binary_name = path + "data" + str(number) + ".benji"
    csv_name = "processed/" + session + "/data" + str(number) + ".csv"
    with open(binary_name, 'br') as f:
        with open(csv_name, 'w') as csv:
            csv.write(
                    "time (s)," + "test number," +
                    "f brake pressure (bar),r brake pressure (bar),steering (degrees)," +
                    "fl shock position (mm),fr shock position (mm),rr shock position (mm),rl shock position (mm)," +
                    "current draw (mA),battery (V)," + 
                    "longitudinal accel (mG),lateral accel (mG),gravity (mG)," +
                    "xgyro (mdps),ygyro (mdps),zgyro (mdps)," +
                    "flsg (lbs),frsg (lbs),rrsg (adc),rlsg (lbs)," +
                    "fl wheel ambient temp (C),fl rotor temp (C),fl wheel speed (rpm)," +
                    "fr wheel ambient temp (C),fr rotor temp (C),fr wheel speed (rpm)," +
                    "rr wheel ambient temp (C),rr rotor temp (C),rr wheel speed (rpm)," +
                    "rl wheel ambient temp (C),rl rotor temp (C),rl wheel speed (rpm)," +
                    "drs status,brake fluid temp (C),throttle load (adc)," +
                    "gps fix,gps longitude,gps latitude,gps speed (m/s)" +
                    "\n")
            data = f.read(4)
            init = int.from_bytes(data, "big")
            last = init
            count = 1
            while data:
                time = int.from_bytes(data, "big")
                last=time
                count += 1

                data = f.read(2) # front brake pressure
                if data is None:
                    break
                fbp = steering(int.from_bytes(data, "big"))
                
                data = f.read(2) # rear brake pressure
                if data is None:
                    break
                rbp = brakePressure(int.from_bytes(data, "big"))

                data = f.read(2) # steering
                if data is None:
                    break
                steer = steering(int.from_bytes(data, "big"))

                data = f.read(2) # fl shock
                if data is None:
                    break
                fls = linearPotentiometer(int.from_bytes(data, "big"))

                data = f.read(2) # fr shock
                if data is None:
                    break
                frs = linearPotentiometer(int.from_bytes(data, "big"))

                data = f.read(2) # rr shock
                if data is None:
                    break
                rrs = linearPotentiometer(int.from_bytes(data, "big"))

                data = f.read(2) # rl shock
                if data is None:
                    break
                rls = linearPotentiometer(int.from_bytes(data, "big"))

                data = f.read(2) # current draw
                if data is None:
                    break
                current = int.from_bytes(data, "big", signed=True) * 1.25

                data = f.read(2) # voltage
                if data is None:
                    break
                battery = int.from_bytes(data, "big") * 1.25 / 1000

                data = f.read(4) # x acce
                if data is None:
                    break
                xAccel  = int.from_bytes(data, "big", signed=True)

                data = f.read(4) # y acce
                if data is None:
                    break
                yAccel  = int.from_bytes(data, "big", signed=True)

                data = f.read(4) # z acce
                if data is None:
                    break
                zAccel  = int.from_bytes(data, "big", signed=True)

                data = f.read(4) # x gyro
                if data is None:
                    break
                xGyro  = int.from_bytes(data, "big", signed=True)

                data = f.read(4) # y gyro
                if data is None:
                    break
                yGyro = int.from_bytes(data, "big", signed=True)

                data = f.read(4) # z gyro
                if data is None:
                    break
                zGyro = int.from_bytes(data, "big", signed=True)

                data = f.read(2) # strain gauges
                if data is None:
                    break
                frsg = fr_sg(int.from_bytes(data, "big"))

                data = f.read(2)
                if data is None:
                    break
                flsg = fl_sg(int.from_bytes(data, "big"))

                data = f.read(2)
                if data is None:
                    break
                rlsg = rl_sg(int.from_bytes(data, "big"))

                data = f.read(2)
                if data is None:
                    break
                rrsg = int.from_bytes(data, "big")

                # fl wheel 
                data = f.read(2)
                if data is None:
                    break
                flw_amb = mlx90614(int.from_bytes(data, "big"))

                data = f.read(2)
                if data is None:
                    break
                flw_rtr = mlx90614(int.from_bytes(data, "big"))

                data = f.read(2)
                if data is None:
                    break
                flw_rpm = int.from_bytes(data, "big")

                # fr wheel 
                data = f.read(2)
                if data is None:
                    break
                frw_amb = mlx90614(int.from_bytes(data, "big"))

                data = f.read(2)
                if data is None:
                    break
                frw_rtr = mlx90614(int.from_bytes(data, "big"))

                data = f.read(2)
                if data is None:
                    break
                frw_rpm = int.from_bytes(data, "big")

                # rr wheel 
                data = f.read(2)
                if data is None:
                    break
                rrw_amb = mlx90614(int.from_bytes(data, "big"))

                data = f.read(2)
                if data is None:
                    break
                rrw_rtr = mlx90614(int.from_bytes(data, "big"))

                data = f.read(2)
                if data is None:
                    break
                rrw_rpm = int.from_bytes(data, "big")

                # rl wheel 
                data = f.read(2)
                if data is None:
                    break
                rlw_amb = mlx90614(int.from_bytes(data, "big"))

                data = f.read(2)
                if data is None:
                    break
                rlw_rtr = mlx90614(int.from_bytes(data, "big"))

                data = f.read(2)
                if data is None:
                    break
                rlw_rpm = int.from_bytes(data, "big")

                # read brake fluid
                data = f.read(2)
                if data is None:
                    break
                brake_fluid = int.from_bytes(data, "big")

                # throttle load
                data = f.read(2)
                if data is None:
                    break
                throttle_load = int.from_bytes(data, "big")        

                # brake load, unused atm
                data = f.read(2)

                # drs
                data = f.read(1)
                if data is None:
                    break
                drs = int.from_bytes(data, "big")

                # gps lon / lat / speed / fix
                data = f.read(4)
                if data is None:
                    break
                gps_lon = int.from_bytes(data, "big") / 10000000

                data = f.read(4)
                if data is None:
                    break
                gps_lat = int.from_bytes(data, "big") / 10000000

                data = f.read(4)
                if data is None:
                    break
                gps_spd = int.from_bytes(data, "big") / 1000

                data = f.read(1)
                if data is None:
                    break
                gps_fix = int.from_bytes(data, "big")

                # test number
                data = f.read(1)
                if data is None:
                    break
                test_no = int.from_bytes(data, "big")



                # read timestamp for next row
                data = f.read(4)

                csv.write(str(time/1000) + "," + str(test_no) + "," + str(fbp) + "," + str(rbp) + "," + str(steer) + "," + 
                            str(fls) + "," + str(frs) + "," + str(rrs) + "," + str(rls) + "," + 
                            str(current) + "," + str(battery) + "," + 
                            str(xAccel) + "," + str(yAccel) + "," + str(zAccel) + "," +
                            str(xGyro) + "," + str(yGyro) + "," + str(zGyro) + "," +
                            str(flsg) + "," + str(frsg) + "," + str(rrsg) + "," + str(rlsg) + "," +
                            str(flw_amb) + "," + str(flw_rtr) + "," + str(flw_rpm) + "," +
                            str(frw_amb) + "," + str(frw_rtr) + "," + str(frw_rpm) + "," +
                            str(rrw_amb) + "," + str(rrw_rtr) + "," + str(rrw_rpm) + "," +
                            str(rlw_amb) + "," + str(rlw_rtr) + "," + str(rlw_rpm) + "," +
                            str(drs) + "," + str(brake_fluid) + "," + str(throttle_load) + "," + 
                            str(gps_fix) + "," + str(gps_lon) + "," + str(gps_lat) + "," + str(gps_spd) +
                            "\n")
            
            print("run length: " + str(last/1000) + " s")
            print(str(1000/((last-init)/count)) + " Hz")
    shock_vel(csv_name)
            

for i in range(1, 21):
    parseBenjiFile(str(i), "data/241003/", "241003")