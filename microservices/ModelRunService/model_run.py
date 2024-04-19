import os
from load_dataset import LoadDataset
from load_model import LoadModel
from process_logs import store_logs
import uuid

run_id = "run_id"
global_model_name = "model_name"

def run_model(dataset_name, model_name):
    # copy the dataset directory
    LoadDataset(dataset_name)

    # copy the model directory
    LoadModel(model_name)

    # check if there is a run.py file in the model directory
    if not os.path.exists(f"model/{model_name}/run.py"):
        return "Error: No run.py file in the model directory"
    
    run_id = uuid.uuid4().hex
    # global_model_name = model_name
    os.makedirs(f"results/{model_name}", exist_ok=True)
    results_path = f'results/{model_name}/{run_id}.txt'
    
    # run the model and store the results in a file
    os.system(f"python model/{model_name}/run.py > {results_path}")

    results = ""
    # return the results as a string
    with open("results.txt", "r") as file:
        results = file.read()

    store_logs(model_name, run_id)

    return results