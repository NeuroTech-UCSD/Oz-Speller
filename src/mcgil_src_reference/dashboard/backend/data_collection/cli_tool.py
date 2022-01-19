from time import time
import datetime

import keyboard
import random
import threading

filename = ''
should_quit = False
fingers = [
    ['left', 'pinkie', 'a'],
    ['left', 'ring finger', 's'],
    ['left', 'middle finger', 'd'],
    ['left', 'index finger', 'f'],
    ['right', 'index finger', 'j'],
    ['right', 'middle finger', 'k'],
    ['right', 'ring finger', 'l'],
    ['right', 'pinkie', ';']
]

def get_date_time():
    return datetime.datetime.now().strftime("%H:%M:%S:%f")

def get_time():
    return round(time() * 1000)

def input_manager():
    global filename, should_quit
    
    while True:
        keystroke = keyboard.read_key()
        if keystroke == 'esc':
            should_quit = True
            break

        if keystroke == 'delete':
            with open(filename, 'w+') as file:
                lines = file.readlines()
                lines = lines[:-2]

        if keystroke == 'backspace':
            with open(filename, 'w+') as file:
                lines = file.readlines()
                lines = lines[:-2]

        with open(filename, 'a') as file:
            file.write('{0}, {1}, {2}\n'.format(get_time(), get_date_time(), keystroke))

def prompts():
    global fingers, should_quit

    if should_quit:
        return
    
    threading.Timer(3.0, prompts).start()

    request = random.choice(fingers)
    print('\nPlease use your {0} {1} to press "{2}"'.format(request[0], request[1], request[2]))

def main():
    global filename
    
    filename = 'logs/log_{0}.txt'.format(get_date_time()).replace(":", "-")
    
    with open(filename, 'w+') as file:
        file.write('timestamp(ms), datetime, keypressed\n')

    input_thread = threading.Thread(target=input_manager)
    input_thread.start()

    prompts()

if __name__ == '__main__':
    main()