# commit hash e4d2eb5
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
                rbp = brakePressure(int.from_bytes(data, "little"))

                data = f.read(2) # steering
                if data is None:
                    break
                ain2 = brakePressure(int.from_bytes(data, "big"))

                data = f.read(2) # fr shock
                if data is None:
                    break

                data = f.read(2) # fl shock
                if data is None:
                    break

                data = f.read(2) # rl shock
                if data is None:
                    break
                rl = linearPotentiometer(int.from_bytes(data, "big"))

                data = f.read(2) # rr shock
                if data is None:
                    break
                rr = linearPotentiometer(int.from_bytes(data, "little"))

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

                data = f.read(8) # placeholder
                if data is None:
                    break

                
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