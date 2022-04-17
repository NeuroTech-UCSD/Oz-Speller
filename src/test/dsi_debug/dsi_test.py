import asyncio
import multiprocessing
import threading
# import multiprocessing
import socketio
from aiohttp import web
import socket, struct
import numpy as np

sio_client = socketio.AsyncClient()
port_number = 4002

class TCPParser: # The script contains one main class which handles DSI-Streamer data packet parsing.

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.done = False
        self.data_log = b''
        self.latest_packets = []
        self.latest_packet_headers = []
        self.latest_packet_data = np.zeros((1,1))
        self.signal_log = np.zeros((1,20))
        self.time_log = np.zeros((1,20))
        self.montage = []
        self.fsample = 0
        self.fmains = 0

        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((self.host,self.port))
        
    def parse_data(self):
        
        # parse_data() receives DSI-Streamer TCP/IP packets and updates the signal_log and time_log attributes
        # which capture EEG data and time data, respectively, from the last 100 EEG data packets (by default) into a numpy array.
        while True:
            data = self.sock.recv(921600)
            self.data_log += data
            if self.data_log.find(b'@ABCD',0,len(self.data_log)) != -1:										# The script looks for the '@ABCD' header start sequence to find packets.
                for index,packet in enumerate(self.data_log.split(b'@ABCD')[1:]):							# The script then splits the inbound transmissio_clientn by the header start sequence to collect the individual packets.
                    self.latest_packets.append(b'@ABCD' + packet)
                for packet in self.latest_packets:
                    self.latest_packet_headers.append(struct.unpack('>BHI',packet[5:12]))
                self.data_log = b''


                for index, packet_header in enumerate(self.latest_packet_headers):		
                    # For each packet in the transmissio_clientn, the script will append the signal data and timestamps to their respective logs.
                    if packet_header[0] == 1:
                        if np.shape(self.signal_log)[0] == 1:												# The signal_log must be initialized based on the headset and number of available channels.
                            self.signal_log = np.zeros((int(len(self.latest_packets[index][23:])/4),20))
                            self.time_log = np.zeros((1,20))
                            self.latest_packet_data = np.zeros((int(len(self.latest_packets[index][23:])/4),1))

                        self.latest_packet_data = np.reshape(struct.unpack('>%df'%(len(self.latest_packets[index][23:])/4),self.latest_packets[index][23:]),(len(self.latest_packet_data),1))
                        self.latest_packet_data_timestamp = np.reshape(struct.unpack('>f',self.latest_packets[index][12:16]),(1,1))

                        # print("Timestamps: " + str(self.latest_packet_data_timestamp))
                        # print("Signal Data: " + str(self.latest_packet_data))

                        self.signal_log = np.append(self.signal_log,self.latest_packet_data,1)
                        self.time_log = np.append(self.time_log,self.latest_packet_data_timestamp,1)
                        self.signal_log = self.signal_log[:,-100:]
                        self.time_log = self.time_log[:,-100:]
                    ## Non-data packet handling
                    if packet_header[0] == 5:
                        (event_code, event_node) = struct.unpack('>II',self.latest_packets[index][12:20])
                        if len(self.latest_packets[index])>24:
                            message_length = struct.unpack('>I',self.latest_packets[index][20:24])[0]
                        print("Event code = " + str(event_code) + "  Node = " + str(event_node))
                        if event_code == 9:
                            montage = self.latest_packets[index][24:24+message_length].decode()
                            montage = montage.strip()
                            print("Montage = " + montage)
                            self.montage = montage.split(',')
                        if event_code == 10:
                            frequencies = self.latest_packets[index][24:24+message_length].decode()
                            print("Mains,Sample = "+ frequencies)
                            mains,sample = frequencies.split(',')
                            self.fsample = float(sample)
                            self.fmains = float(mains)
            self.latest_packets = []
            self.latest_packet_headers = []
            

class Server:
    def __init__(self):
        # basic AsyncServer setup
        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")
        self.app = web.Application()
        self.sio.attach(self.app)
        self.port = 4002

    def start_server(self):
        web.run_app(self.app, host='0.0.0.0', port=self.port)  # we're using local host here

async def fetch_data():
    dsi_parser = TCPParser('localhost',8844)
    data_thread = threading.Thread(target=dsi_parser.parse_data)
    data_thread.daemon = True
    data_thread.start()
    # data_process = multiprocessing.Process(target=dsi_parser.parse_data)
    # data_process.daemon = True
    # data_process.start()
    file = open('./eeg.csv', 'w')
    file.write('time, ch1, ch2, ch3, ch4, ch5, ch6, ch7\n')
    file.close()

    # latest_signal_log = np.copy(dsi_parser.signal_log)
    # latest_time_log = np.copy(dsi_parser.time_log)
    while True:
        latest_signal_log = np.copy(dsi_parser.signal_log)[:,:-1].T
        latest_time_log = np.copy(dsi_parser.time_log)[:,:-1].T
        dsi_parser.signal_log = dsi_parser.signal_log[:,-1:]
        dsi_parser.time_log = dsi_parser.time_log[:,-1:]
        latest_data = np.concatenate((latest_time_log, latest_signal_log[:,:8]), axis=1)
        with open('./eeg.csv', 'a') as csv_file: # 'a' for append
            np.savetxt(csv_file, latest_data, delimiter=', ')
        await sio_client.sleep(0.1)

async def fetch_fake_data():
    file = open('./fake_eeg.csv', 'w')
    file.write('ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8\n')
    file.close()
    while True:
        fake_data = np.random.rand(5,8)
        with open('./fake_eeg.csv', 'a') as csv_file: # 'a' for append
            np.savetxt(csv_file, fake_data, delimiter=', ')
        await sio_client.sleep(0.1) 

async def start_dsi():
    await sio_client.connect(f'http://localhost:{port_number}')
    sio_client.start_background_task(fetch_data)
    await sio_client.wait()

if __name__ == "__main__":
    server = Server()
    # asyncio.run(server.start_server())
    # server.start_server()
    server_thread = threading.Thread(target=server.start_server)
    server_thread.daemon = True
    server_thread.start()
    # server_process = multiprocessing.Process(target=server.start_server)
    # server_process.daemon = True
    # server_process.start()
    asyncio.run(start_dsi())
    