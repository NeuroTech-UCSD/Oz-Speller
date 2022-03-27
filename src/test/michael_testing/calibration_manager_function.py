import asyncio
import random

import socketio
import time
import datetime
from itertools import permutations

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
    config = await sio.call(
        'calibration ready')  # wait for the server to confirm that server
    # is ready. Server would send config when it's ready


async def send_trial():
    print('calibration manager initiated -- Start sending trials ...')
    # ============= use config instead of hard coding ================
    num_blocks = config["NUM_BLOCKS"]
    trial_duration = config["TRIAL_DURATION"] / 1000  # convert to seconds
    inter_trial_interval = config["INTER_TRIAL_INTERVAL"] / 1000  # convert to seconds
    # ================================================================

    tic = time.time()
    characters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                  'U', 'V', 'W', 'X', 'Y', 'Z']
    stored_values = []
    for i in range(num_blocks):
        a = datetime.datetime.now()
        random_index = random.randint(0, len(characters) - 1)
        while random_index in stored_values:
            random_index = random.randint(0, len(characters) - 1)
        stored_index = random_index
        stored_values.append(stored_index)

        s = "%s:%s.%s" % (a.minute, a.second, str(a.microsecond)[:3])
        print(
            f'calibration manager: send trial {characters[random_index]} to server, time diff since last trial: {time.time() - tic:.3f}, {s}')
        tic = time.time()
        await sio.emit('generate trial', characters[random_index])
        await asyncio.sleep(trial_duration)
        await sio.emit('trial end', True)
        await asyncio.sleep(inter_trial_interval)


async def main():
    await sio.connect(f'http://localhost:{PORT}')
    await sio.start_background_task(ready)
    await sio.call('all components ready')  # calibration will ask the server if all the components are loaded
    sio.start_background_task(send_trial)
    await sio.wait()


asyncio.run(main())
