import asyncio
import socketio
from aiohttp import web
from multiprocessing import Process, Queue, Lock
import numpy as np
from dsi import TCPParser
from utils import stream_random_data, stream_dsi_data

class Server:
    def __init__(self, queue):
        # basic AsyncServer setup
        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")
        self.app = web.Application()
        self.sio.attach(self.app)
        # setting up data queue
        self.queue = queue

    async def background_task(self):
        """Example of how to send server generated events to clients."""
        while True:
            if self.queue.empty():
                await self.sio.sleep(0.1)
            else:
                queue_item = self.queue.get()
                await self.sio.emit("background", queue_item['background'])
                await self.sio.emit("background2", queue_item['background2'])
                while not queue.empty(): # lousy way of clearing the queue
                    queue.get()


    def start_server(self):
        self.sio.start_background_task(target=self.background_task)
        web.run_app(self.app, host='0.0.0.0', port='4002')

# def run_task(task):
#     asyncio.run(task.get_coro())

if __name__ == '__main__':
    queue = Queue()
    server = Server(queue)
    dsi_parser = TCPParser('localhost',8844)
    # stream_random_data_thread = Process(target=stream_random_data, args=(queue,))
    # stream_random_data_thread.daemon = True
    # stream_random_data_thread.start()
    stream_dsi_data_thread = Process(target=stream_dsi_data, args=(dsi_parser, queue,))
    stream_dsi_data_thread.daemon = True
    stream_dsi_data_thread.start()
    server.start_server()

    # exiting the program
    # stream_random_data_thread.join()
    stream_dsi_data_thread.join()