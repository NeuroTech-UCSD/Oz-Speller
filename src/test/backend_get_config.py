# from flask import Flask, render_template
# from flask_socketio import SocketIO, Namespace, emit

# # Set this variable to "threading", "eventlet" or "gevent" to test the
# # different async modes, or leave it set to None for the application to choose
# # the best option based on installed packages.
# async_mode = "threading"

# app = Flask(__name__)
# # app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")
# socketio.run(app,port=4002,host='0.0.0.0')

# async def my_function_handler(data):
#     print(data)
#     await socketio.emit('response', 'ok')

# socketio.on_event('ready', my_function_handler)

# if __name__ == '__main__':
#     socketio.run(app)

##############################################################################

import socketio
from aiohttp import web

class Server:
    def __init__(self):
        # basic AsyncServer setup
        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")
        self.app = web.Application()
        self.sio.attach(self.app)

    async def get_config_handler(self, sid, data):
        print(data)
        # await self.sio.emit('response', '123')

    def start_server(self):
        self.sio.on('form submitted', self.get_config_handler)
        web.run_app(self.app, host='0.0.0.0', port='4002')


if __name__ == '__main__':
    server = Server()
    server.start_server()

