import pandas as pd
import json

def ProcessLogs(model_name, run_id, results_path):
    # Get the variables to be tracked from config file in model  
    with open(f"models/{model_name}/config.json") as f:
        config = json.load(f)

    variables = config["variables"]

    # Get the logs from the log file
    with open(results_path) as f:
        logs = f.readlines()

    # Scrape the variables from the logs
    data = {}
    for log in logs:
        for variable in variables:
            if variable in log:
                data[variable] = log.split("=")[1]

    # Save the data to a csv file
    df = pd.DataFrame(data, index=[0])
    df.to_csv(f"results/{model_name}/{run_id}_data.csv", index=False)

    StoreLogs(model_name, run_id, results_path)

def StoreLogs(model_name, run_id, results_path):
    # Store the logs in a MongoDB database