#!/usr/bin/python
import RPi.GPIO as GPIO
from pymodbus.client.sync import ModbusSerialClient as ModbusClient 
import time
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def relay_set(defect):
    if defect == "normal":
	 GPIO.output(2, GPIO.HIGH)
	 GPIO.output(3, GPIO.LOW)
	 GPIO.output(4, GPIO.LOW)
         #GPIO.output(17, GPIO.LOW)

    elif defect == "open":
	 GPIO.output(2, GPIO.LOW)
	 GPIO.output(3, GPIO.LOW)
	 GPIO.output(4, GPIO.LOW)
         #GPIO.output(17, GPIO.LOW)

    elif defect == "short":
	 GPIO.output(2, GPIO.HIGH)
	 GPIO.output(3, GPIO.LOW)
	 GPIO.output(4, GPIO.HIGH)
         #GPIO.output(17, GPIO.LOW)

    elif defect == "contact":
         GPIO.output(2, GPIO.LOW)
	 GPIO.output(3, GPIO.HIGH)
	 GPIO.output(4, GPIO.LOW)
         #GPIO.output(17, GPIO.LOW)

client = ModbusClient(method = 'rtu', port='/dev/ttyXRUSB0', baudrate=115200)
client.connect()


GPIO.setmode(GPIO.BCM)

# define faults and their corresponding pin number
condition_cycle = {"normal", "open", "short", "contact"}

# initialize relay to make sure all ports are connected
pin_num = [2,3,4]
for i in pin_num:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)


output = {"Date/Time":[],"Condition":[],"voltage":[], "current":[], "power":[]}
minute = 15
t_end = time.time() + 60*minute
count = 1

condition = "normal"
relay_set(condition)

while time.time() < t_end:

    print(count)

    result = client.read_input_registers(0x3100, 6, unit=1)
    solarvoltage = float(result.registers[0]/100.0)
    solarcurrent = float(result.registers[1]/100.0)
    solarpower = float(result.registers[2]/100.0)
    output["Date/Time"].append(time.asctime(time.localtime(time.time())))
   
    output["voltage"].append(solarvoltage)
    output["current"].append(solarcurrent)
    output["power"].append(solarpower)
    output["Condition"].append(condition)

    #if count in [60*1, 60*3, 60*5, 60*7, 60*9]:
#	condition = "open"
#        relay_set(condition)
#	print("Open circuit!")

    #if count in [60*3, 60*7, 60*11]:
    #    condition = "short"
    #    relay_set(condition)
    #    print("Short circuit!")

    #if count in [60*3, 60*7, 60*11]:
    #    condition = "contact"
    #    relay_set(condition)
    #    print("Contact circuit!")

    #if count in [60*0, 60*2, 60*4, 60*6, 60*8, 60*10]:
        #condition = "normal"
        #relay_set(condition)
	#print("Circuit back to normal")


    if count % 60 == 0:
	data = pd.DataFrame(dict([(k, pd.Series(v)) for k,v in output.items()]))
	export_csv = data.to_csv("normal_data.csv", index=True, header=True)
    count += 1
    time.sleep(1)

#plt.plot(output["power"])
#plt.plot(output["voltage"])
#plt.plot(output["current"])
#plt.legend(["Power(W)", "Voltage(V)", "Current(A)"])
#plt.legend(["Voltage(V)"])
#plt.show()


client.close()


