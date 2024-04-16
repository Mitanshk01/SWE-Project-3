from flask import Flask, request, jsonify
from flask_cors import CORS
from model_run import ModelRun
import os

app = Flask(__name__)
CORS(app)

@app.route('/run_model', methods=['POST'])
def run_model():
    request_data = request.json
    dataset_name = request_data['dataset_name']
    model_name = request_data['model_name']  # format repo/model
    model_run = ModelRun(dataset_name, model_name)
    result = model_run.run()
    return jsonify(result)

if __name__ == '__main__':
    # make model and data directory
    os.makedirs('model', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    app.run(host='localhost', port=5000)


