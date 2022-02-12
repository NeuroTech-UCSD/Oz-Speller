import asyncio
import socketio
import time
import datetime

sio = socketio.AsyncClient()
PORT = 4002


@sio.event
async def connect():
    print('connected')


@sio.event
async def connect_error(e):
    print(e)


@sio.event
async def disconnect():
    await sio.disconnect()
    print('disconnected')


async def ready():
    global config
    await asyncio.sleep(2.5)  # simulate loading all resources for the frontend
    config = await sio.call(
        'frontend ready')  # wait for the server to confirm that server is ready. \
    # Server would send config when it's ready


@sio.event
async def start_flashing(data):
    a = datetime.datetime.now()
    s = "%s:%s.%s" % (a.minute, a.second, str(a.microsecond)[:3])
    print(f'trial received: {data} -- {s}, start flashing')
    # ============= use config instead of hard coding ================
    # num_trials = 7
    trial_duration = 3
    # inter_trial_interval = 2
    # ================================================================

    await asyncio.sleep(trial_duration)  # simulate flashing


async def main():
    await sio.connect(f'http://localhost:{PORT}')
    await sio.start_background_task(ready)
    await sio.wait()


asyncio.run(main())
