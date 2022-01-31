from flask import Flask, request
from flask_cors import CORS
import os, time, json

app = Flask(__name__)
CORS(app)
 
@app.route('/prompt')
def prompt():
    global file_path

    datetime = request.args.get('datetime') # YYYY-MM-DD-HH:MM:SS:msms
    timestamp = request.args.get('timestamp') # absolute time (ms)
    hand = request.args.get('hand') # right | left
    finger = request.args.get('finger') # pinkie | ring finger | middle finger | index finger
 
    with open(file_path, 'a') as f:
        f.write(', '.join([datetime, timestamp, 'prompt_end', hand, finger, '']) + '\n')
 
    return 'OK'

@app.route('/custom-prompt')
def custom_prompt():
    global file_path

    datetime = request.args.get('datetime') # YYYY-MM-DD-HH:MM:SS:msms
    timestamp = request.args.get('timestamp') # absolute time (ms)
    prompt = request.args.get('prompt') # custom prompt
    hand = request.args.get('hand')
    finger = request.args.get('finger')
    key = request.args.get('key')
 
    with open(file_path, 'a') as f:
        if (not hand is None) and (not finger is None) and (not key is None):
            f.write(', '.join([datetime, timestamp, 'prompt_end', hand, finger, key ]) + '\n')
        else:
            f.write(', '.join([datetime, timestamp, 'prompt_end', prompt ]) + '\n')
    return 'OK'
 
@app.route('/data-collection')
def keystroke():
    global file_path

    datetime = request.args.get('datetime') # YYYY-MM-DD-HH:MM:SS:msms
    timestamp = request.args.get('timestamp') # absolute time (ms)
    key = request.args.get('key') # key pressed
 
    with open(file_path, 'a') as f:
        f.write(', '.join([datetime, timestamp, 'keystroke', '', '', key]) + '\n')
 
    return 'OK'

@app.route('/new-session')
def new_session():    

    global file_path

    datetime = request.args.get('datetime') # YYYY-MM-DD-HH:MM:SS:msms
    timestamp = request.args.get('timestamp') # absolute time (ms)
    subject_id = request.args.get('id') # subject id of person recording
    mode = request.args.get('mode') # recording mode
    trial = request.args.get('trial') # trial number
    prompts = request.args.get('prompts') # prompts, defined if mode is guided or in air
    notes = request.args.get('notes') # any additional notes
    year,month,day,rest = datetime.split('-')

    session_filepath = f'data/{year}-{month}-{day}'
    if not os.path.exists(session_filepath):
        os.makedirs(session_filepath)

    file_path = os.path.join(session_filepath, datetime.replace(':', '-') + '.txt')
    print(file_path)

    metadata = {
        "id": subject_id,
        "trial": trial,
        "mode": mode,
        "datetime": datetime,
        "timestamp": timestamp,
        "prompts": prompts,
        "notes": notes
     }

    with open(file_path, 'w+') as f:  # writing JSON object
        json.dump(metadata, f, indent=4)    
        f.write('\ndatetime, timestamp, event, hand, finger, key\n')

    return 'OK'
 
if __name__ == '__main__':
    app.run()