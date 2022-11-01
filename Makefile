.PHONY: clean

VENV = venv
PYTHON = $(VENV)/Scripts/python
PIP = ./$(VENV)/Scripts/pip

app: $(VENV)/Scripts/activate
	$(PYTHON) scripts/oz-speller_without-headset.py

speller: $(VENV)/Scripts/activate
	$(PYTHON) scripts/oz-speller_without-headset.py

chatbot: $(VENV)/Scripts/activate
	$(PYTHON) scripts/oz-speller_without-headset.py



$(VENV)/Scripts/activate: requirements.txt
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt


clean:
	rm -rf __pycache__
	rm -rf $(VENV)
