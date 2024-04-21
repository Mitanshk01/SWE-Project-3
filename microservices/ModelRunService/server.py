from flask import Flask, request, jsonify
from flask_cors import CORS
from model_run import train_model
import os

app = Flask(__name__)
CORS(app)

@app.route('/train_model', methods=['POST'])
def train():
    request_data = request.json
    user_id = request_data['user_id']
    repo_name = request_data['repoName']  # format repo/model
    run_id = request_data['run_id']
    model_run = train_model(user_id, repo_name, run_id)
    result = model_run.run()
    return jsonify(result)

if __name__ == '__main__':
    # make model and data directory
    os.makedirs('model', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    app.run(host='localhost', port=5000)


