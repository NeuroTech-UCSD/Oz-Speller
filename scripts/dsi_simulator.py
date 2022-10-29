import time
import asyncio
import socketio
import random

sio = socketio.AsyncClient()
PORT = 4002
ISI = 3  # inter-stimulus-interval in seconds


@sio.event
async def connect():
    print('dsi simulator connected')


@sio.event
async def connect_error(e):
    print('Connection error:', e)


@sio.event
async def disconnect():
    print('dsi simulator disconnected')


# generate a random letter in the range x - y
def rand_letter(x='a', y='z'):
    return chr(random.randint(ord(x), ord(y)))


async def _dsi_simulator():
    """

    :return:
    """
    N = 5
    while True:
        await sio.sleep(ISI)
        dsi_message = ''
        for i in range(N):
            dsi_message += rand_letter()
        print('DSI simulator sending message:', dsi_message)
        await sio.emit('forward_message', dsi_message, namespace='/dsi')


async def dsi_simulator():
    host = '100.84.31.10'
    await sio.connect(f'http://{host}:{PORT}', namespaces=['/', '/dsi'])
    await sio.start_background_task(_dsi_simulator)
    await sio.wait()


if __name__ == '__main__':
    asyncio.run(dsi_simulator())
