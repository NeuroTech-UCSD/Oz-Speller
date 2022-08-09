import serial
import time

import sys
use_dsi7 = True
data = []
run_count = 0
first_call = True
sys.path.append('src') # if run from the root project directory



# dsi_serial.baudrate = 115200
# dsi_serial.port = 'COM2'
# dsi_serial.open()


## DSI-7
if use_dsi7:
    import dsi, ctypes, multiprocessing, time
    import numpy as np
    from pylsl import local_clock
    from threading import Thread, Event
    SampleCallback = ctypes.CFUNCTYPE( None, ctypes.c_void_p, ctypes.c_double, ctypes.c_void_p )
    @SampleCallback
    def ExampleSampleCallback_Signals( headsetPtr, packetTime, userData ):
        global run_count
        global data
        global first_call
        h = dsi.Headset( headsetPtr )
        sample_data = [packetTime] # time stamp
        sample_data.extend([ch.ReadBuffered() for ch in h.Channels()]) # channel voltages
        data.append(sample_data)
        run_count += 1
        if first_call:
            if sample_data[1] > 1e15: # if Pz saturation error happens
                quit()
            with open("meta.csv", 'w') as csv_file:
                # csv_file.write(str(time.time()) + '\n')
                csv_file.write(str(local_clock()) + '\n')
            first_call = False
        if run_count >= 300: # save data every second
            run_count = 0
            data_np = np.array(data)
            with open("eeg.csv", 'a') as csv_file:
                np.savetxt(csv_file, data_np, delimiter=', ')
            data = []
    def record():
        args = getattr( sys, 'argv', [ '' ] )
        if sys.platform.lower().startswith( 'win' ): default_port = 'COM8' #COM4, COM8, COM9
        else:                                        default_port = '/dev/cu.DSI7-0009.BluetoothSeri'
        # first command-line argument: serial port address
        if len( args ) > 1: port = args[ 1 ]
        else: port = default_port
        # second command-line argument:  name of the Source to be used as reference, or the word 'impedances'
        if len( args ) > 2: ref = args[ 2 ]
        else: ref = ''
        headset = dsi.Headset()
        headset.Connect(port)
        headset.SetSampleCallback( ExampleSampleCallback_Signals, 0 )
        headset.StartDataAcquisition()
        with open("eeg.csv", 'w') as csv_file:
            csv_file.write('time, '+', '.join([ ch.GetName()  for ch in headset.Channels() ])+'\n')
        while True:
            headset.Idle(2.0)
    if __name__ == "__main__": 
        # recording = multiprocessing.Process(target=record,daemon=True)
        recording = Thread(target=record,daemon=True)
        recording.start()
        time.sleep(12)


dsi_serial = serial.Serial('COM2',115200)
for i in range(10):
    msg = b'\x01\xe1\x01\x00\x01'
    dsi_serial.write(msg)
    time.sleep(1)