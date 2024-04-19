import pandas as pd
import json
import zipfile
import requests

def store_logs(model_name, run_id):
    # Store the file in OneDrive
    logs_path = "results/{model_name}/{run_id}_logs.csv"
    results_path = f"results/{model_name}/{run_id}.txt"

    # Zip the file and upload it to OneDrive
    with zipfile.ZipFile(f"results/{model_name}/{run_id}_logs.zip", 'w') as zip_ref:
        zip_ref.write(logs_path)

    with zipfile.ZipFile(f"results/{model_name}/{run_id}_data.zip", 'w') as zip_ref:
        zip_ref.write(results_path)

    drive_api_url = 'https://graph.microsoft.com/v1.0/me/drive/root:/FolderName/Filename:/content'
    drive_api_url += "/users"

    # Upload the zip file to OneDrive
    upload_one_drive(run_id, logs_path, drive_api_url+"/" + logs_path)
    upload_one_drive(run_id, results_path, drive_api_url+"/" + results_path)

    update_database(drive_api_url+"/" + logs_path, drive_api_url+"/" + results_path, run_id)

    print(f"Logs for run {run_id} stored successfully.")


def upload_one_drive(run_id, path, api_url):
    # Upload the zip file to OneDrive

    access_token = 'your_access_token'  # replace with your actual access token
    headers = {'Authorization': 'Bearer ' + access_token}
    params = {'@name.conflictBehavior': 'rename'}
    data = open(path, 'rb').read()

    response = requests.put(
        api_url,
        headers=headers,
        params=params,
        data=data
    )

    if response.status_code == 201:
        print(f"Logs for run {run_id} stored successfully.")
    else:
        print(f"Failed to store logs for run {run_id}. Error: {response.text}")


def update_database(onedrive_link_logs, onedrive_link_results, run_id):
    # Update the database with the link to the logs

    api_url = 'http://127.0.0.1:8000/logs'

    params = {
        'onedrive_link_logs': onedrive_link_logs,
        'onedrive_link_results': onedrive_link_results,
        'run_id': run_id
    }

    response = requests.post(api_url, json=params)

    if response.status_code == 201:
        print("Database updated successfully.")
        return True
    else:
        print(f"Failed to update database. Error: {response.text}")
        return False
    
