import serial, threading, multiprocessing, time
from pylsl import local_clock
import numpy as np
# arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1)
arduino = serial.Serial(port='COM3', baudrate=19200, timeout=.1)
# arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)
arduino_call_num = 0
datalist = []
data_save_num = 0
with open("light_amp.csv", 'w') as csv_file:
    csv_file.write('time, light_amp\n')
def record_light_amp():
    global arduino_call_num
    global datalist
    global data_save_num
    while True:
        try:
            # data = arduino.readline().decode('ascii')[:-1]
            data = int.from_bytes(arduino.read(), "big")
            if data > 100:
                data = 0
            if arduino_call_num < 100:
                arduino_call_num+=1
                continue
            elif arduino_call_num == 100:
                arduino_call_num+=1
                with open("meta.csv", 'w') as csv_file:
                    csv_file.write('1,1,'+str(local_clock()) + '\n')
                    # csv_file.write('0,0,'+str(time.time()) + '\n')
            # datalist.append([time.time(),data])
            datalist.append([local_clock(),data])
            data_save_num += 1
            if data_save_num > 7000:
                datalist_np = np.array(datalist)
                with open("light_amp.csv", 'a') as csv_file:
                    # csv_file.write(data)
                    # csv_file.write(str(local_clock())+', '+str(data)+'\n')
                    # csv_file.write(str(time.time())+', '+str(data)+'\n')
                    # np.savetxt(csv_file, datalist_np, delimiter=', ')
                    # np.savetxt(csv_file, datalist_np, delimiter=', ', fmt=['%1.4e','%1.4e'])
                    # np.savetxt(csv_file, datalist_np, delimiter=', ', fmt=['%1.7f','%d']) 
                    np.savetxt(csv_file, datalist_np, delimiter=', ', fmt=['%.14e','%d'])
                    data_save_num = 0
                    datalist = []
            # time.sleep(0.001)
        except UnicodeDecodeError and ValueError:
            pass
record_light_amp()