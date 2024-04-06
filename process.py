# commit hash 624a240
from transfer import linearPotentiometer, brakePressure

def parseBenjiFile(number: int):
    binary_name = "raw/data" + str(number) + ".benji"
    csv_name = "processed/data" + str(number) + ".csv"
    with open(binary_name, 'br') as f:
        with open(csv_name, 'w') as csv:
            csv.write("time (s),f brake pressure (bar),r brake pressure (bar),rl shock position (mm),rr shock position (mm),current draw(mA),battery (V),longitudinal accel (mG),lateral accel (mG), graivty (mG), ain2 (adc)\n")
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
                fbp = brakePressure(int.from_bytes(data, "big"))
                
                data = f.read(2) # rear brake pressure
                if data is None:
                    break
                rbp = brakePressure(int.from_bytes(data, "big"))

                data = f.read(2) # steering
                if data is None:
                    break
                steer = brakePressure(int.from_bytes(data, "big"))

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

                data = f.read(4) # x acce
                if data is None:
                    break
                xGyro  = int.from_bytes(data, "big", signed=True)

                data = f.read(4) # y acce
                if data is None:
                    break
                yGyro = int.from_bytes(data, "big", signed=True)

                data = f.read(4) # z acce
                if data is None:
                    break
                zGyro = int.from_bytes(data, "big", signed=True)


                data = f.read(2) # strain gauges
                if data is None:
                    break
                frsg = int.from_bytes(data, "big")

                data = f.read(2)
                if data is None:
                    break
                flsg = int.from_bytes(data, "big")

                data = f.read(2)
                if data is None:
                    break
                rlsg = int.from_bytes(data, "big")

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

                data = f.read(1)
                if data is None:
                    break
                test_no = int.from_bytes(data, "big")


                # read timestamp for next row
                data = f.read(4)

                csv.write(str(time/1000) + "," + str(fbp) + "," + str(rbp) + "," + 
                            str(rl) + "," + str(rr) + "," + 
                            str(current) + "," + str(battery) + "," + 
                            str(yAccel) + "," + str(xAccel) + "," + str(zAccel) + "," + str(ain2) +
                            "\n")
            
            print("run length: " + str(last) + " ms")
            print(str(1000/((last-init)/count)) + " Hz")


# useful files: 81,82,83,84,85,86
#parseBenjiFile(85)
for i in range(81, 87):
    parseBenjiFile(i)
