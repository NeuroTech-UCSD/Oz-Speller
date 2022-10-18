import sys
import socketio
from aiohttp import web
import json
from datetime import datetime
import numpy as np
from datetime import datetime


def reset_content(filepath: str):
    with open(filepath, "w") as file:
        json_obj = {'content': []}
        json.dump(json_obj, file)


def get_content(filepath: str):
    with open(filepath, "r") as file:
        content = json.load(file)
        return content


def update_content(filepath: str, sender: str, text: str):
    n_chars_in_line = 40  # number of characters in a line
    json_obj = get_content(filepath)
    json_obj['content'].append(
        {'sender': sender, 'text': text, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
         'n_lines': np.ceil(len(text) / n_chars_in_line) + 2})

    with open(filepath, "w") as file:
        json.dump(json_obj, file)


class DSI(socketio.AsyncNamespace):

    def on_connect(self, sid, environ):
        print('dsi connected')

    def on_disconnect(self, sid):
        print('dsi disconnected')

    async def on_forward_message(self, sid, data):
        message = data
        print('Received DSI message:', data)
        # writing message to local back_to_front.json for chat history
        update_content('states/back_to_front.json', sender='Patient', text=message)
        # forward message to frontend
        await self.emit('get_message', message, namespace='/caretaker')


class Caretaker(socketio.AsyncNamespace):

    def on_connect(self, sid, environ):
        print('caretaker connected')

    def on_disconnect(self, sid):
        print('cartaker disconnected')

    async def on_forward_message(self, sid, data):
        message = data
        print('Received caretaker message:', message)
        # writing message to local back_to_front.json
        update_content('states/back_to_front.json', sender='Caretaker', text=message)


class Server:
    def __init__(self):
        # basic AsyncServer setup
        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")
        self.app = web.Application()
        self.sio.attach(self.app)
        self.sio.register_namespace(DSI('/dsi'))
        self.sio.register_namespace(Caretaker('/caretaker'))
        self.port = 4002
        self.config = {'patient_id': 12345, 'date': None}

    async def get_config(self, sid):
        return self.config

    async def display_config(self, sid, data):
        print(data)

    def start_server(self):
        reset_content('states/back_to_front.json')
        self.sio.on('get config', self.get_config)
        self.sio.on('form submitted', self.display_config)
        web.run_app(self.app, host='0.0.0.0', port=self.port)  # we're using local host here


if __name__ == '__main__':
    server = Server()
    server.start_server()
