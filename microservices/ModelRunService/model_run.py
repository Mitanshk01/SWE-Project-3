import os

def ModelRun(dataset_name, model_name):
    # copy the dataset directory
    LoadDataset(dataset_name)

    # copy the model directory
    LoadModel(model_name)

    # check if there is a run.py file in the model directory
    if not os.path.exists(f"model/{model_name}/run.py"):
        return "Error: No run.py file in the model directory"
    
    # run the model and store the results in a file
    os.system(f"python model/{model_name}/run.py > results.txt")

    results = ""
    # return the results as a string
    with open("results.txt", "r") as file:
        results = file.read()

    ProcessLogs(model_name)

    return results



