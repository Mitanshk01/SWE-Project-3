import pandas as pd
import json
import zipfile
import requests

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
    # Store the file in OneDrive
    file_path = "results/{model_name}/{run_id}_data.csv"

    # Zip the file and upload it to OneDrive
    with zipfile.ZipFile(f"results/{model_name}/{run_id}_data.zip", 'w') as zip_ref:
        zip_ref.write(file_path)

    UploadOneDrive(model_name, run_id)

    print(f"Logs for run {run_id} stored successfully.")


def UploadOneDrive(model_name, run_id):
    # Upload the zip file to OneDrive

    api_url = 'https://graph.microsoft.com/v1.0/me/drive/root:/FolderName/Filename:/content'

    access_token = 'your_access_token'  # replace with your actual access token
    headers = {'Authorization': 'Bearer ' + access_token}
    params = {'@name.conflictBehavior': 'rename'}
    data = open(f"results/{model_name}/{run_id}_data.zip", 'rb').read()

    response = requests.put(
        api_url,
        headers=headers,
        params=params,
        data=data
    )

    if response.status_code == 201:
        if UpdateDB(model_name, run_id):
            print(f"Logs for run {run_id} stored successfully.")
        else:
            print("Failed to update database but uploaded on OneDrive")
    else:
        print(f"Failed to store logs for run {run_id}. Error: {response.text}")


def UpdateDB(onedrive_link, run_id):
    # Update the database with the link to the logs

    api_url = 'localhost:8000/logs'

    params = {
        'onedrive_link': onedrive_link,
        'run_id': run_id
    }

    response = requests.post(api_url, params=params)

    if response.status_code == 200:
        print("Database updated successfully.")
        return True
    else:
        print(f"Failed to update database. Error: {response.text}")
        return False
    
UpdateDB("<link>", "DSJFBJESFN")
