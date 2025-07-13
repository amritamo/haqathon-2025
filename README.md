# haQathon-2025

## Install requirements
Navigate to the gui-application folder and run
`pip install -r requirements.txt`

## Model from HF
download the model from HF and put it under a directory called `llama_local`

## To run the GUI:
1) first run the flask server: open one terminal and run
`python llama_api.py`

2) once this connects to localhost successfully, then open another terminal and run
`python gui-application\ai-tutor.py`
