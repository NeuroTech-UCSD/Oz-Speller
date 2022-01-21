import asyncio
import socketio
from aiohttp import web
from multiprocessing import Process, Queue, Lock
import time
import random
import numpy as np

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")
app = web.Application()
sio.attach(app)

async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(0.1)
        count += 1
        # print(sid1)
        await sio.emit("background", {
            'timestamp': time.time(),
            # 'value' : random.random()
            'value' : list(np.random.rand(8))
            })
        await sio.emit("background2", {
            'timestamp': time.time(),
            # 'value' : random.random()
            'value' : list(np.random.rand(8))
            })

# app.router.add_static('/static', 'static')
# app.router.add_get('/', index)
@sio.on('connect')
async def test_connect(sid, environ):
    await sio.emit('my response', {'data': 'Connected', 'count': 0}, room=sid)
    # print(sid)
    # print(type(sid))


@sio.on('disconnect')
def test_disconnect(sid):
    print('Client disconnected')

# def start_server():
#     # sio.start_background_task(target=background_task)
#     web.run_app(app, host='0.0.0.0', port='4002')

# def run_task(task):
#     asyncio.run(task.get_coro())

if __name__ == '__main__':
    sio.start_background_task(target=background_task)
    # task.print_stack()
    # task2 = Process(target=start_server)
    # task2.daemon = True
    # task2.start()
    # print(task.done())
    # loop = asyncio.new_event_loop()
    # loop.run_until_complete(task)
    # asyncio.run(task.get_coro())
    # task.print_stack()
    web.run_app(app, host='0.0.0.0', port='4002')
    # web.run_app(app)