# previous_time = time.time()
import sys
sys.path.append('src')
import dsi, ctypes, multiprocessing, threading, time
SampleCallback = ctypes.CFUNCTYPE( None, ctypes.c_void_p, ctypes.c_double, ctypes.c_void_p )
first_call = True
@SampleCallback
def ExampleSampleCallback_Signals( headsetPtr, packetTime, userData ):
    # global run_count
    # global data
    global first_call
    # global previous_time
    previous_time = time.time()
    h = dsi.Headset( headsetPtr )
    # sample_data = [packetTime] # time stamp
    # sample_data = [time.time()] # time stamp
    # sample_data.extend([ch.ReadBuffered() for ch in h.Channels()[:-1]]) # channel voltages
    sample_data = [ch.ReadBuffered() for ch in h.Channels()[:-1]]
    # data.append(sample_data)
    # run_count += 1
    if first_call:
        if sample_data[1] > 1e15: # if Pz saturation error happens
            quit()
        with open("meta.csv", 'w') as csv_file:
            csv_file.write('0,0,'+str(time.time()) + '\n')
        first_call = False
    # if run_count >= 30:
    #     run_count = 0
    #     data_np = np.array(data)
    #     with open("eeg.csv", 'a') as csv_file:
    #         np.savetxt(csv_file, data_np, delimiter=', ')
    #     data = []

    # data_np = np.array([sample_data])
    # with open("eeg.csv", 'a') as csv_file:
    #     np.savetxt(csv_file, data_np, delimiter=', ')

    with open("eeg.csv", 'a') as csv_file:
        csv_file.write(str(time.time())+', ')
        for stuff in sample_data[:-1]:
            csv_file.write(str(stuff)+', ')
        csv_file.write(str(sample_data[-1])+'\n')

    # time.sleep(1/300-(time.time()-previous_time))
    # on a standard Windows installation, the smallest interval you may delay is 10 - 13 milliseconds
    # time.sleep(0.000001)
    # previous_time=time.time()

def record():
    args = getattr( sys, 'argv', [ '' ] )
    if sys.platform.lower().startswith( 'win' ): default_port = 'COM4'
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
        csv_file.write('time, '+', '.join([ ch.GetName()  for ch in headset.Channels()[:-1] ])+'\n')
    while True:
        # headset.Idle(2.0)
        headset.Idle(5000.0)
        # pass
if __name__ == "__main__": 
    # recording = multiprocessing.Process(target=record,daemon=True)
    # recording = threading.Thread(target=record,daemon=True)
    # recording.start()
    # time.sleep(6)
    record()