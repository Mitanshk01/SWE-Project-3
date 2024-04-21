import os
from load_dataset import LoadDataset
from load_model import LoadModel
from process_logs import store_logs
import uuid

run_id = "run_id"
global_model_name = "model_name"

def train_model(user_id, repo_name, run_id, model_file_id, data_file_id):
    # copy the dataset directory
    print("[In train_model] ")
    LoadDataset(user_id, repo_name, run_id, data_file_id)
    LoadModel(user_id, repo_name, run_id, model_file_id)

    # # check if there is a run.py file in the model directory
    if not os.path.exists(f"model/{model_file_id}/train.py"):
        return "Error: No run.py file in the model directory"
    
    # run_id = uuid.uuid4().hex
    # # global_model_name = model_name
    # os.makedirs(f"results/{run_id}", exist_ok=True)
    # results_path = f'results/{run_id}/{run_id}.txt'
    
    # # # run the model and store the results in a file
    # os.system(f"python model/{run_id}/run.py > {results_path}")

    # results = ""
    # # return the results as a string
    # with open("results.txt", "r") as file:
    #     results = file.read()

    # store_logs(user_id, repo_name, run_id, results_path)

    return results