.PHONY: clean

VENV = venv
PYTHON = $(VENV)/Scripts/python.exe
PIP = ./$(VENV)/Scripts/pip

env:
	echo APP_PORT=$(APP_PORT) >> .env
	echo HOST_ADDR=$(HOST_ADDR) >> .env

chatbot_docker:
	docker pull ghcr.io/neurotech-ucsd/conversational-agents-for-hospitalized-agents:main

caretaker_docker:
	docker pull ghcr.io/neurotech-ucsd/ssvep-ui:master

app: $(VENV)/Scripts/activate chatbot_docker caretaker_docker env
	nohup $(PYTHON) scripts/server.py &
	nohup $(PYTHON) scripts/dsi.py &
	nohup $(PYTHON) scripts/chatbot_listener.py &
	nohup docker run -e APP_PORT=$(APP_PORT) -e HOST_ADDR=$(HOST_ADDR) ghcr.io/neurotech-ucsd/conversational-agents-for-hospitalized-agents:main &
	nohup docker run -p 3000:3000 -e REACT_APP_HOST=$(HOST_ADDR) -e APP_PORT=$(APP_PORT) ghcr.io/neurotech-ucsd/ssvep-ui:master &
	echo "Waiting for 35 seconds for docker containers to spawn"
	sleep 35
	$(PYTHON) scripts/oz-speller_without-headset.py

speller: $(VENV)/Scripts/activate
	$(PYTHON) scripts/oz-speller_without-headset.py

speller_sim: $(VENV)/Scripts/activate chatbot_docker env
	nohup $(PYTHON) scripts/server.py &
	nohup $(PYTHON) scripts/dsi.py &
	nohup $(PYTHON) scripts/chatbot_listener.py &
	nohup docker run -e APP_PORT=$(APP_PORT) -e HOST_ADDR=$(HOST_ADDR) ghcr.io/neurotech-ucsd/conversational-agents-for-hospitalized-agents:main &
	nohup docker run -p 3000:3000 -e REACT_APP_HOST=$(HOST_ADDR) -e APP_PORT=$(APP_PORT) ghcr.io/neurotech-ucsd/ssvep-ui:master &
	echo "Waiting for 35 seconds for docker containers to spawn"
	sleep 35
	$(PYTHON) scripts/dsi_manual_simulator.py


$(VENV)/Scripts/activate: requirements.txt
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

clean:
	rm -rf __pycache__
	rm -rf $(VENV)
