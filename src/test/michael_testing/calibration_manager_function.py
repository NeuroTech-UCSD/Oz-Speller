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
    config = await sio.call(
        'calibration ready')  # wait for the server to confirm that server
    # is ready. Server would send config when it's ready


async def send_trial():
    print('calibration manager initiated -- Start sending trials ...')
    # ============= use config instead of hard coding ================
    num_trials = 7
    trial_duration = 3
    inter_trial_interval = 2
    # ================================================================

    tic = time.time()
    for i in range(num_trials):
        await sio.emit('generate trial', chr(i + 97))
        a = datetime.datetime.now()
        s = "%s:%s.%s" % (a.minute, a.second, str(a.microsecond)[:3])
        print(
            f'calibration manager: send trial {chr(i + 97)} to server, time diff since last trial: {time.time() - tic:.3f}, {s}')
        tic = time.time()
        await asyncio.sleep(trial_duration + inter_trial_interval)


async def main():
    await sio.connect(f'http://localhost:{PORT}')
    await sio.start_background_task(ready)
    await sio.call('all components ready')  # calibration will ask the server if all the components are loaded
    sio.start_background_task(send_trial)
    await sio.wait()


asyncio.run(main())
