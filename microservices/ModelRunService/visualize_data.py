from flask import Flask, request, jsonify
from load_dataset import LoadDataset
import pandas as pd

app = Flask(__name__)

@app.route('/fetch-table-headings', methods=['GET'])
def fetch_table_headings():
    repo_name = request.args.get('repo_name')
    file_id = request.args.get('file_id')
    
    file_path = load_dataset_viz(repo_name, file_id)
    
    # Load the dataset using Pandas
    df = pd.read_csv(file_path)
    
    # Extract column names
    column_names = df.columns.tolist()
    
    return jsonify(column_names)

@app.route('/fetch-column-details', methods=['GET'])
def fetch_column_details():
    repo_name = request.args.get('repo_name')
    file_id = request.args.get('file_id')
    column_name = request.args.get('column_name')
    
    file_path = load_dataset_viz(repo_name, file_id)
    
    # Load the dataset using Pandas
    df = pd.read_csv(file_path)
    
    # Check if the column exists
    if column_name in df.columns:
        # Extract data for the specified column
        column_data = df[column_name].tolist()
        return jsonify(column_data)
    else:
        return jsonify({"error": "Column not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
