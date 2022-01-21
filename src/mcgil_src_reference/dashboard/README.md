# Dashboard-NeuroTech Software

Contains the code for the dashboard frontend, real-time backend, and data collection backend.

Run `start_data_collection.sh` to start the dashboard with the data collection backend.

Run `start_real_time.sh` to start the dashboard with the real-time backend.

# Dashboard Frontend

The requirements for running the dashboard are `node v12` and `yarn v1`.

To start the Dashboard, you can run the following:

```
# change to the prod-frontend directory
cd prod-frontend

# install the necessary node packages
yarn install

# start the create-react-app
yarn start
```

## `yarn start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

## `yarn build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

# Real-time Backend

## Architecture

![Architecture Image](https://raw.githubusercontent.com/NTX-McGill/NeuroTechX-McGill-2020/main/src/dashboard/backend/real_time/architecture_diagram.jpg)

## Usage

### Interaction

Keyboard inputs:

-   **"space":** select the most likely word
-   **"backspace":** delete last character if one exists, otherwise last word
-   **"C-c":** exit
-   **"0":** Enter word selection mode. Then select a word by pressing a lower case char associated with the desired index
-   **lower case char:** input finger associated with character

### Setup

Environment (requires python3):

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Download a [finger number prediction model](https://github.com/NTX-McGill/NeuroTechX-McGill-2020/tree/main/offline/models) into \`NeuroTech-ML/models\` and set the `model_file` variable in `backend.py`.

Run:

```bash
python backend.py
```

In order for the backend to run with `finger_mode = True`, Start the data stream in OpenBCIv4. In the networking widget, switch to LSL and set Stream 1 with the following settings:

-   **Data Type:** "Timeseries"
-   **Name:** obci<sub>eeg1</sub>
-   **Type:** EEG
-   **# Chan:** 8

Then press "Start" in the networking widget.

### Parameters

There are two configurable variables in backend.py

-   **server_mode:** Indicates whether or not to emit predictions and data over socketio
-   **finger_mode:** When true, reads signal data from OpenBCI and converts it to finger numbers. When false, reads keypresses from stdin and converts them to finger numbers.

## Connecting with AR

We maintain the state of the word being built in the backend, and send the frontend instructions for updating the UI accordingly.

Backend state:

-   current finger word
-   finger selection mode

Frontend state:

-   most likely words
-   finger selection mode
-   previously typed words
-   most recently typed character

## Instructions

### Most Likely Words

Instruction to update the most likely words in the frontend

```json
{
  "message": "most_likely_words",
  "words": ["word1", "word2", ...],
}
```

### Enter Word Selection Mode

Instruction to enter word selection mode in the frontend

```json
{
  "message": "enter_word_selection"
}
```

### Capture word

Instruction to capture/select a word.

```json
{
  "message": "select_word",
  "word": "word2"
}
```

### Delete Word

Instruction to delete a word backwards

```json
{
  "message": "delete_word",
}
```

### Exit Typing Mode

Instruction to leave typing mode

```json
{
  "message": "leave_typing_mode"
}
```

### Error Message

Instruction to display error message. Potential errors:

-   could not enter word selection mode
-   could not select word

```json
{
  "message": "error_message",
  "error_code": "could_not_select_word"
}
```

## prediction_server.py

Contains the PredictionServer class. Functionality:

-   reads finger numbers from a queue
-   emits data for the dashboard and virtual reality clients on port 40002 via a socketio server
-   builds word predictions from a dictionary of most common english words

# Data Collection Backend

## Dashboard-NeuroTech Backend


In `backend/`, create a virtual environment using `venv` in Python:

```
python3 -m venv env
```
Add your env folder in .gitignore

Start the virtual environment using:
```
source env/bin/activate
```

To close the environment use `deactivate`

To install all of the necessary dependencies in it use:

```text
pip install -r {path_to}/requirements.txt
```

When finished check your dependencies with:

```text
pip list
```

Start the backend with
```
python webapp_backend.py
```
