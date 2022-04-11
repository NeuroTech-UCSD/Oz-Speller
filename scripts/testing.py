import subprocess
import os
import asyncio
import sys
from sys import executable
from subprocess import Popen, CREATE_NEW_CONSOLE

Popen([executable,  os.path.join(os.getcwd(), 'src', 'test', 'michael_testing', 'server.py')])
Popen([executable,  os.path.join(os.getcwd(), 'src', 'test', 'michael_testing', 'dsi_collection_function.py')])

