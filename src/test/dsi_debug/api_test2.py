import asyncio
import socketio
from aiohttp import web
import sys, ctypes
import threading
import numpy as np
import dsi

sio_client = socketio.AsyncClient()
port_number = 4002
data = []
run_count = 0

class Server:
    def __init__(self, port_number=4002):
        # basic AsyncServer setup
        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")
        self.app = web.Application()
        self.sio.attach(self.app)
        self.port = port_number

    def start_server(self):
        web.run_app(self.app, host='0.0.0.0', port=self.port)

SampleCallback = ctypes.CFUNCTYPE( None, ctypes.c_void_p, ctypes.c_double, ctypes.c_void_p )
@SampleCallback
def ExampleSampleCallback_Signals( headsetPtr, packetTime, userData ):
    global run_count
    global data
    h = dsi.Headset( headsetPtr )
    sample_data = [packetTime] # time stamp
    sample_data.extend([ch.ReadBuffered() for ch in h.Channels()]) # channel voltages
    data.append(sample_data)
    run_count += 1
    if run_count >= 300:
        run_count = 0
        # print(data)
        data_np = np.array(data)
        with open("myfile.csv", 'a') as csv_file:
            np.savetxt(csv_file, data_np, delimiter=', ')
        data = []

async def record():
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
    with open("myfile.csv", 'w') as csv_file:
        csv_file.write('time, '+', '.join([ ch.GetName()  for ch in headset.Channels() ])+'\n')
    while True:
        headset.Idle(2.0)

async def start_dsi():
    await sio_client.connect(f'http://localhost:{port_number}')
    sio_client.start_background_task(record)
    await sio_client.wait()

if __name__ == "__main__":
    server = Server()
    server_thread = threading.Thread(target=server.start_server)
    server_thread.daemon = True
    server_thread.start()
    asyncio.run(start_dsi())