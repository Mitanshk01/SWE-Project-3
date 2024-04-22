import pandas as pd
import json
import zipfile
import requests
import os

def upload_run_to_repo(user_id, repo_name, run_id, results_file, log_file):
    # API endpoint URL
    api_url = 'http://localhost:8004/upload_run_to_repo'
    
    data = {
        'userid': user_id,
        'repo_name': repo_name,
        'run_id': run_id,
    }

    # files = {
    #     'results_file': open(results_file, 'rb'),
    #     'log_file': open(log_file, 'rb')
    # }

    results_file_obj = open(results_file, 'rb')
    log_file_obj = open(log_file, 'rb')

    multipart_form_data = {
        'userid': (None, data['userid']),
        'repo_name': (None, data['repo_name']),
        'run_id': (None, data['run_id']),
        'results_file': (results_file, results_file_obj, 'application/zip'),
        'log_file': (log_file, log_file_obj, 'application/zip'),
    }

    try:
        response = requests.post(api_url,files = multipart_form_data)
        if response.status_code == 200:
            print("Run files uploaded successfully.")
        else:
            print(f"An error occurred: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        
    finally:
        results_file_obj.close()
        log_file_obj.close()

def store_logs(user_id, repo_name, run_id):
    # Store the file in OneDrive
    logs_path = f"results/{run_id}/logs.csv"
    results_path = f"results/{run_id}/results.txt"

    os.makedirs("results/zips", exist_ok=True)

    log_zip = f"results/zips/{run_id}_logs.zip"
    results_zip = f"results/zips/{run_id}_results.zip"

    with zipfile.ZipFile(log_zip, 'w') as zip_ref:
        zip_ref.write(logs_path)

    with zipfile.ZipFile(results_zip, 'w') as zip_ref:
        zip_ref.write(results_path)

    upload_run_to_repo(user_id, repo_name, run_id, results_zip, log_zip)

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
    
