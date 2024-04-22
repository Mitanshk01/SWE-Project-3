from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/train', methods=['POST'])
def train_model():
    # Get the training script file name and dataset name from the request
    data = request.json
    training_script = data.get('training_script')
    dataset = data.get('dataset')

    if not training_script or not dataset:
        return jsonify({'error': 'Missing required parameters'}), 400

    # Execute the training script with the provided dataset name
    try:
        subprocess.run(['python', training_script, dataset], check=True)
        return jsonify({'message': 'Training completed successfully'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Training failed: {e.stderr}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
