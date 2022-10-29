import time
import asyncio
import socketio
import random
import yaml

sio = socketio.AsyncClient()
PORT = 4002
ISI = 3  # inter-stimulus-interval in seconds
old_content = current_content = ''


@sio.event
async def connect():
    print('dsi connected')


@sio.event
async def connect_error(e):
    print('Connection error:', e)


@sio.event
async def disconnect():
    print('dsi disconnected')


def update_content():
    with open("states/front_to_back.yaml", "r") as file:
        try:
            global current_content
            current_content = yaml.safe_load(file)
            # print(current_content['text'])
        except yaml.YAMLError as exc:
            print(exc)


def reset_content():
    with open("states/front_to_back.yaml", "w") as file:
        try:
            out = {
                'text': ''
            }
            yaml.dump(out, file)
        except yaml.YAMLError as exc:
            print(exc)


def send_detected() -> bool:
    if '\u2709' in current_content['text']:
        return True
    else:
        return False


async def _dsi():
    """

    :param include_enter: whether to include enter key every N characters, N is hard set in the code
    :return:
    """
    reset_content()
    while True:
        await sio.sleep(0.8)
        update_content()
        if send_detected():
            message = current_content['text'][:-1]
            print('Sending message:', message)
            await sio.emit('forward_message', message, namespace='/dsi')
            reset_content()




async def dsi():
    await sio.connect(f'http://192.168.167.132:{PORT}', namespaces=['/', '/dsi'])
    await sio.start_background_task(_dsi)


if __name__ == '__main__':
    asyncio.run(dsi())
