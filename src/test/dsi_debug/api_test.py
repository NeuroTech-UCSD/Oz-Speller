from asyncio import run_coroutine_threadsafe
import sys, io, time, ctypes
import multiprocessing
import dsi

SampleCallback = ctypes.CFUNCTYPE( None, ctypes.c_void_p, ctypes.c_double, ctypes.c_void_p )
var1 = []
sample_str = ''
sys_stdout = sys.stdout
io_stdout = io.StringIO()
run_count = 0


def IfStringThenNormalString( x ):
    if str is not bytes and isinstance( x, bytes ): x = x.decode( 'utf-8' )
    return x

@SampleCallback
def ExampleSampleCallback_Signals( headsetPtr, packetTime, userData ):
    global run_count
    global sample_str
    h = dsi.Headset( headsetPtr )
    strings = [ '%s=%+08.2f' % ( IfStringThenNormalString( ch.GetName() ), ch.ReadBuffered() ) for ch in h.Channels() ]
    sample_str += ( '%8.3f:   ' % packetTime ) + ', '.join( strings ) + '\n'
    run_count += 1
    if run_count >= 300:
        run_count = 0
        print(sample_str)
        with open("myfile.txt", 'a') as file1:
            file1.write(sample_str)
        sample_str = ''
    # print( ( '%8.3f:   ' % packetTime ) + ', '.join( strings ) )
    # sys.stdout.flush()
    # var1.append( ( '%8.3f:   ' % packetTime ) + ', '.join( strings ) )
    # userData.append( ( '%8.3f:   ' % packetTime ) + ', '.join( strings ) )
    # userData += ( '%8.3f:   ' % packetTime ) + ', '.join( strings )

def record():
    args = getattr( sys, 'argv', [ '' ] )
    if sys.platform.lower().startswith( 'win' ): default_port = 'COM4'
    else:                                        default_port = '/dev/cu.DSI7-0009.BluetoothSeri'

    # first command-line argument: serial port address
    if len( args ) > 1: port = args[ 1 ]
    else: port = default_port

    # second command-line argument:  name of the Source to be used as reference, or the word 'impedances'
    if len( args ) > 2: ref = args[ 2 ]
    else: ref = ''
    headset = dsi.Headset()
    headset.Connect(port)
    var3 = ''
    headset.SetSampleCallback( ExampleSampleCallback_Signals, var3 )
    # sys.stdout = io_stdout
    headset.StartDataAcquisition()
    while True:
        headset.Idle(2.0)
        print(var3)

if __name__ == '__main__':
    with open("myfile.txt", "w") as file1:
        file1.write('')
    recording = multiprocessing.Process(target=record,daemon=True)
    recording.start()
    while True:
        try:
            # var2 = io_stdout.getvalue()
            # io_stdout.flush()
            # with open("myfile.txt", 'a') as file1:
            #     file1.write(var2)
            # print(len(var1))
            # if len(var1) > 0: print(var1[-1])
            time.sleep(0.5)
        except KeyboardInterrupt:
            exit()
    