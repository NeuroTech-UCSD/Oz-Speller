import asyncio
import socketio
import time
import datetime

sio = socketio.AsyncClient()
PORT = 4002
global current_trial
global prev
prev = datetime.datetime.now()
current_trial = '*'  # can replace with 0


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


@sio.event
async def change_trial(data):
    global current_trial
    global prev
    current_trial = data  # data is just a char
    a = datetime.datetime.now()
    diff = a - prev
    diff_s = "%s" % (diff.total_seconds())
    print(diff_s)
    prev = a
    s = "%s:%s.%s" % (a.minute, a.second, str(a.microsecond)[:3])
    print(f'trial changed to \"{data}\" -- {s}')


async def ready():
    global config
    config = await sio.call(
        'dsi ready')  # wait for the server to confirm that server is ready. Server would send config when it's ready


async def fetch_data():
    '''
    This function will continue fetch data from dsi headset and \
    (1) write the data to the csv
    (2) send it (deque snapshot with k elements with num_channels size each, k should be >= 1) to remote
    Note: we can move (2) outside and have the server ask for it instead
    :return:
    '''
    print('dsi collection initiated -- Start recording data ...')
    # ============= use config instead of hard coding ================
    num_trials = 7
    trial_duration = 3
    inter_trial_interval = 2
    # ================================================================
    while True:
        a = datetime.datetime.now()
        s = "%s:%s.%s" % (a.minute, a.second, str(a.microsecond)[:3])
        print(f'current trial {current_trial} -- {s}')
        await sio.sleep(2)  # provide window for other thread to run




async def main():
    await sio.connect(f'http://localhost:{PORT}')
    await sio.start_background_task(ready)
    sio.start_background_task(fetch_data)
    await sio.wait()  # this line is important, do not delete


asyncio.run(main())
