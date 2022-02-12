import asyncio
import time
import datetime

num_trials = 7
trial_duration = 3
inter_trial_interval = 2


async def calibration_manager():
    print('calibration manager initiated -- Start sending trials ...')
    tic = time.time()
    for i in range(num_trials):
        a = datetime.datetime.now()
        s = "%s:%s.%s" % (a.minute, a.second, str(a.microsecond)[:3])
        print(
            f'calibration manager: send trial {chr(i + 97)} to server, time diff since last trial: {time.time() - tic:.3f}, {s}')
        tic = time.time()
        await asyncio.sleep(trial_duration + inter_trial_interval)


async def frontend_flashing():
    print('frontend flashing initiated')


async def dsi_collection():
    print('dsi collection initiated')
    while True:
        await asyncio.sleep(1)  # simulating the delay of sending data from dsi headset to dsi_collection
        # print('dsi_collection: send ith data to the server')


async def server():
    frontend = asyncio.create_task(frontend_flashing())
    calibration = asyncio.create_task(calibration_manager())
    dsi = asyncio.create_task(dsi_collection())

    # await frontend
    # await calibration
    await dsi


asyncio.run(server())
