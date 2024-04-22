from flask import request, jsonify
from load_dataset_viz import LoadDatasetViz
import pandas as pd

def fetch_table_headings(user_id, repo_name, data_file_id):
    LoadDatasetViz(repo_name, data_file_id)
    
    dataset_path = f"repos/{repo_name}/data/train.csv"
    df = pd.read_csv(dataset_path)
    
    column_names = df.columns.tolist()
    
    return column_names

def fetch_column_details(user_id, repo_name, data_file_id, col_name):
    LoadDatasetViz(repo_name, data_file_id)

    dataset_path = f"repos/{repo_name}/data/train.csv"
    df = pd.read_csv(dataset_path)
    
    # Check if the column exists
    if col_name in df.columns:
        # Extract data for the specified column
        column_data = df[col_name].tolist()
        return column_data
    else:
        return None
