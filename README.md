# haQathon-2025

## Install requirements
Navigate to the gui-application folder and run
`pip install -r requirements.txt`

## Model from AI toolkit on VS code
1) Download the model from the models 'Catalog'. The model name is: `qnn-deepseek-r1-distill-qwen-1.5b`. 
2) Once it appears in your 'My Models' section, start the ONNX runtime by right-clicking and selecting `Start server`. 
3) Right-click and copy the endpoint for the ONNX runtime and change this in the `send_query()` module in the `gui-application/ai-tutor.py` file (there's a comment there where it needs to be changed)
4) Once the server is up and running, run the GUI with: `python gui-application/ai-tutor.py`