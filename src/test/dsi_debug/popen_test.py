from subprocess import Popen, PIPE
import os
import signal
import time

# p = Popen(['C:/Users/simon/Downloads/dsi2lsl-win/dsi2lsl.exe', '--port=COM4'],shell=True,stdin=PIPE)
p = Popen([os.path.join(os.getcwd(), 'src', 'dsi2lsl-win', 'dsi2lsl.exe'), '--port=COM4'],shell=True,stdin=PIPE)

time.sleep(5)
os.kill(p.pid, signal.CTRL_C_EVENT)
