import socketio
from aiohttp import web
import asyncio
from collections import deque
import numpy as np
import time


class Server:
    def __init__(self):
        # basic AsyncServer setup
        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")
        self.app = web.Application()
        self.sio.attach(self.app)
        self.port = 4002
        self.config = None  # dictionary of experiment setup
        self.calibration_ready = False
        self.dsi_ready = False
        self.frontend_ready = False
        self.state = None
        self.plot_buffer = deque()  # buffer for the plot function. Once filled to plot_buffer_size,
        # will always have shape (plot_buffer_size, num_channels) when we do np.array(self.plot_buffer)
        self.plot_buffer_size = 1000  # number of time points for the buffer

    '''
    Check if all the components are ready to start the experiment
    '''

    async def check_components_ready(self, sid):
        while (self.dsi_ready and self.calibration_ready and self.frontend_ready) is False:
            await self.sio.sleep(5)  # will check if all components are ready every 5 seconds
        print('All components are ready')

    async def get_config_handler(self, sid, data):
        self.config = data
        print(data)

    async def send_dsi_ready_signal(self, sid):
        self.dsi_ready = True
        self.sio.start_background_task(target=self.send_plot_to_frontend)
        print(f'dsi is ready')
        return self.config

    async def send_calibration_ready_signal(self, sid):
        '''
        We have to start calibration signal last as it will await all ready signals
        '''
        self.calibration_ready = True
        print('calibration is ready')
        return self.config

    async def send_frontend_ready_signal(self, sid):
        self.frontend_ready = True
        print('frontend is ready')
        return self.config

    async def generate_trial(self, sid, data):
        '''
        :param sid:
        :param data: str, 'a', 'b', etc
        :return:
        '''
        await self.sio.emit('start_flashing', data)  # Note: if start flashing has no delay, we can put change_trial
        # in a separate function and parallelize these two requests
        await self.sio.emit('change_trial', data)

    async def receive_data(self, sid, data):
        '''

        :param sid:
        :param data: 2d deque, k elements each with size num_channels, k is an arbitrary positive int >= 1
        :return:
        '''
        data = np.array(data) # turn list to numpy
        # case: if buffer not filled
        if len(self.plot_buffer) < self.plot_buffer_size:
            num_extra = len(self.plot_buffer) + len(data[0]) - self.plot_buffer_size
            for i in range(num_extra):
                self.plot_buffer.popleft()
            for i in range(len(data[0])):
                self.plot_buffer.append(data[:][i])

        # case: if buffer filled
        else:
            for i in range(len(data[0])):
                self.plot_buffer.popleft()
                self.plot_buffer.append(data[:][i])

    async def send_plot_to_frontend(self):
        """Example of how to send server generated events to clients."""
        while True:
            if self.plot_buffer: # if not empty
                # print(np.array(self.plot_buffer)[0].shape)
                await self.sio.emit('time series', {
                                                    'timestamp': time.time(),
                                                    'value' : list(np.array(self.plot_buffer)[-1])
                                                    })
            await self.sio.sleep(0.2)

    def start_server(self):
        self.sio.on('form submitted', self.get_config_handler)
        self.sio.on('dsi ready', self.send_dsi_ready_signal)
        self.sio.on('calibration ready', self.send_calibration_ready_signal)
        self.sio.on('frontend ready', self.send_frontend_ready_signal)
        self.sio.on('generate trial', self.generate_trial)
        self.sio.on('all components ready', self.check_components_ready)
        self.sio.on('receive data', self.receive_data)
        web.run_app(self.app, host='0.0.0.0', port=self.port)  # we're using local host here


if __name__ == '__main__':
    server = Server()
    # asyncio.run(server.start_server())
    server.start_server()
