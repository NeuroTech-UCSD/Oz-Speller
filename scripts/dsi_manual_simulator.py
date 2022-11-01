import time
import asyncio
import socketio
import random
import settings


sio = socketio.AsyncClient()
PORT = settings.Configuration.app['port']
HOST = settings.Configuration.app['host']

@sio.event
async def connect():
    print('dsi manual simulator connected')


@sio.event
async def connect_error(e):
    print('Connection error:', e)


@sio.event
async def disconnect():
    print('dsi manual simulator disconnected')

async def _dsi_simulator():
    """

    :return:
    """
    while True:
        await sio.sleep(1)
        print("Enter a message for dsi:", end=" ")
        dsi_message = str(input())
        print('DSI simulator sending message:', dsi_message)
        await sio.emit('forward_message', dsi_message, namespace='/dsi')


async def dsi_simulator():
    await sio.connect(f'http://{HOST}:{PORT}', namespaces=['/', '/dsi'])
    await sio.start_background_task(_dsi_simulator)
    await sio.wait()


if __name__ == '__main__':
    asyncio.run(dsi_simulator())
