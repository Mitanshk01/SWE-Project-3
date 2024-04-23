import os
from load_dataset import LoadDataset
from load_model import LoadModel
from process_logs import store_logs
from model_log import ModelLog
import pandas as pd
import uuid
import subprocess

run_id = "temp_run_id"
global_model_name = "temp_model_name"
global_run_id = "temp_id"
global_repo_name = "temp_repo_name"
global_user_id = "temp_user_id"


def train_model(user_id, repo_name, run_id, model_file_id, data_file_id):
    # copy the dataset directory
    print("[In train_model] ")
    LoadDataset(user_id, repo_name, run_id, data_file_id)
    LoadModel(user_id, repo_name, run_id, model_file_id)

    print("Dataset and model loaded")

    # # check if there is a run.py file in the model directory
    if not os.path.exists(f"repos/{repo_name}/model/train.py"):
        print("Error: No train.py file in the model directory")
        return "Error: No train.py file in the model directory"
    

    os.makedirs(f"results/{run_id}", exist_ok=True)
    results_path = f'results/{run_id}/results.txt'
    log_path = f'results/{run_id}/logs.csv'

    # save the run_id to a run_id.txt file in repos/{repo_name}/model folder
    with open(f"repos/run_id.txt", "w") as file:
        print("Writing run_id to file")
        file.write(run_id)
        print("Write successful.")
    
    print("Running model")

    command = f"PYTHONPATH=$PYTHONPATH:. RUN_ID={run_id} python repos/{repo_name}/model/train.py"

    with open(results_path, 'w') as f:
        result = subprocess.run(command, shell=True, stdout=f, stderr=subprocess.PIPE, text=True)

    print("stderr:", result.stderr)



    # return None

    # os.system(f"PYTHONPATH=$PYTHONPATH:. RUN_ID={run_id} python repos/{repo_name}/model/train.py > {results_path}")
    
    # os.system(f"python repos/{repo_name}/model/train.py > {results_path}")

    print("Model run complete")

    results = ""
    # return the results as a string
    with open(results_path, "r") as file:
        results = file.read()

    # write empty DataFrame to log file
    if not os.path.exists(log_path):
        pd.DataFrame().to_csv(log_path, index=False)

    print("Results: ", results)

    # TODO 
    store_logs(user_id, repo_name, run_id)

    return results

def finetune_model(user_id, repo_name, run_id, model_file_id, data_file_id):
    train_model(user_id, repo_name, run_id, model_file_id, data_file_id)

def infer_model(user_id, repo_name, run_id, model_file_id, data_file_id):
   # copy the dataset directory
    print("[In train_model] ")
    LoadDataset(user_id, repo_name, run_id, data_file_id)
    LoadModel(user_id, repo_name, run_id, model_file_id)

    print("Dataset and model loaded")

    # # check if there is a run.py file in the model directory
    if not os.path.exists(f"repos/{repo_name}/model/infer.py"):
        print("Error: No train.py file in the model directory")
        return "Error: No train.py file in the model directory"
    

    os.makedirs(f"results/{run_id}", exist_ok=True)
    results_path = f'results/{run_id}/results.txt'
    log_path = f'results/{run_id}/logs.csv'

    # save the run_id to a run_id.txt file in repos/{repo_name}/model folder
    with open(f"repos/run_id.txt", "w") as file:
        print("Writing run_id to file")
        file.write(run_id)
        print("Write successful.")
    
    print("Running model")

    command = f"PYTHONPATH=$PYTHONPATH:. RUN_ID={run_id} python repos/{repo_name}/model/infer.py"

    with open(results_path, 'w') as f:
        result = subprocess.run(command, shell=True, stdout=f, stderr=subprocess.PIPE, text=True)

    print("stderr:", result.stderr)

    # os.system(f"PYTHONPATH=$PYTHONPATH:. RUN_ID={run_id} python repos/{repo_name}/model/infer.py > {results_path}")
    
    # # os.system(f"python repos/{repo_name}/model/train.py > {results_path}")

    print("Model run complete")

    results = ""
    # return the results as a string
    with open(results_path, "r") as file:
        results = file.read()

    # write empty DataFrame to log file
    if not os.path.exists(log_path):
        pd.DataFrame().to_csv(log_path, index=False)

    print("Results: ", results)

    # TODO 
    store_logs(user_id, repo_name, run_id)

    return results