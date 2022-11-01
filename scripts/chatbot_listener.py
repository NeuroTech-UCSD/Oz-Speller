import sys
import socketio
from aiohttp import web
import json
from datetime import datetime
import numpy as np
from datetime import datetime
import asyncio
import settings

PORT = settings.Configuration.app['port']
HOST = settings.Configuration.app['host']


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


sio = socketio.AsyncClient()


@sio.event
async def connect():
    print('dsi helper connected')


@sio.event
async def connect_error(e):
    print('Connection error:', e)


@sio.event
async def disconnect():
    print('dsi helper disconnected')


@sio.event(namespace='/chatbot_listener')
async def update_content_channel(message):
    """

    :return:
    """
    print('update content:', message)
    update_content('states/back_to_front.json', message['sender'], message['text'])


async def chatbot():
    reset_content('states/back_to_front.json')
    await sio.connect(f'http://{HOST}:{PORT}', namespaces=['/', '/chatbot_listener'])
    await sio.wait()


if __name__ == '__main__':
    asyncio.run(chatbot())
