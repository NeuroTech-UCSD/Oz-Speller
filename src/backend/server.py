import socketio
from aiohttp import web
from multiprocessing import Process, Queue, Lock

class Server:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*", sync_handlers=True)
        self.app = web.Application()
        self.sio.attach(self.app)

    def startServer(self):
        task = self.sio.start_background_task(self.interactive_mode)
        web.run_app(self.app, host='0.0.0.0', port='4002')

    async def send_test(self):
        print('test')
        await self.sio.emit('send_test', {'data': 'hello'})

    # Interactive mode
    # server_mode indicates that we should send messages to the frontend
    async def interactive_mode(self):
        await self.send_test()
        print('123')
        # while True:
        #     await self.send_test()
            # await self.sio.sleep(0.01)

def consumer():
    serv1 = Server()
    serv1.startServer()



# async def test1(sid):
#     await sio.emit('send_test', 'hello')

if __name__ == "__main__":
    
    proc1 = Process(target=consumer, args=())
    proc1.daemon = True
    proc1.start()
    proc1.join()