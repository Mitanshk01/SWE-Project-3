from flask import Flask, request, jsonify
from flask_cors import CORS
from model_run import train_model
from visualize_data import fetch_table_headings, fetch_column_details
import os
from model_run import global_model_name, global_repo_name, global_run_id, global_user_id

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
# CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})

@app.route('/train_model', methods=['POST'])
def train():
    request_data = request.json
    print("[In 5000] : ", request_data)
    user_id = request_data['user_id']
    repo_name = request_data['repo_name']  # format repo/model
    run_id = request_data['run_name']
    model_file_id = request_data['model_file_id']
    data_file_id = request_data['data_file_id']
    model_run = train_model(user_id, repo_name, run_id, model_file_id, data_file_id)

    print(f"Trained model for user {user_id}, repo {repo_name}, run {run_id}")

    return jsonify({'status': 'success'})
    # return jsonify(result)


@app.route('/fetch_headings', methods=['GET'])
def fetch_headings():
    request_data = request.json
    user_id = request_data['user_id']
    repo_name = request_data['repo_name']
    data_file_id = request_data['data_file_id']

    column_names = fetch_table_headings(user_id, repo_name, data_file_id)
    
    # # Load the dataset using Pandas
    # df = pd.read_csv(file_path)
    
    # # Extract column names
    # column_names = df.columns.tolist()
    
    return jsonify(column_names)

@app.route('/fetch_column', methods=['GET'])
def fetch_column_details(user_id, repo_name, data_file_id):
    request_data = request.json
    user_id = request_data['user_id']
    repo_name = request_data['repo_name']
    col_name = request_data['col']

    column = fetch_column_details(user_id, repo_name, data_file_id, col_name)
    
    # Check if the column exists
    if column:
        # Extract data for the specified column
        return jsonify(column)
    else:
        return jsonify({"error": "Column not found"}), 404

if __name__ == '__main__':
    app.run(host='localhost', port=5000)


