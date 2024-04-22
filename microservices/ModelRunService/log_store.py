from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_URI = "mongodb+srv://swayamagrawal:rkcvMxl2OYhj0Qb0@cluster0.eihouhl.mongodb.net/?retryWrites=true&w=majority"

class MongoDBService:
    def __init__(self, uri: str):
        self.client = MongoClient(uri)
        self.db: Database = self.client['log_storage']
        self.collection: Collection = self.db['logs']

    def create_log_entry(self, run_id: str, onedrive_link_logs: str, onedrive_link_results: str):
        log_entry = {
            'run_id': run_id,
            'onedrive_link_logs': onedrive_link_logs,
            'onedrive_link_results': onedrive_link_results
        }
        print("Creating log entry   ", log_entry)
        result = self.collection.insert_one(log_entry)
        return result.inserted_id

    def get_log_entry(self, run_id: str):
        query = {'run_id': run_id}
        log_entry = self.collection.find_one(query)
        return log_entry

    def update_log_entry(self, run_id: str, onedrive_link_logs: str, onedrive_link_results: str):
        query = {'run_id': run_id}
        update = {"$set": {'onedrive_link_logs': onedrive_link_logs, 'onedrive_link_results': onedrive_link_results}}
        result = self.collection.update_one(query, update)
        return result.modified_count

    def delete_log_entry(self, run_id: str):
        query = {'run_id': run_id}
        result = self.collection.delete_one(query)
        return result.deleted_count

mongo_service = MongoDBService(DB_URI)

@app.route('/logs', methods=['POST'])
def create_log():
    data = request.json
    run_id = data['run_id']
    onedrive_link_results = data['onedrive_link_results']
    onedrive_link_logs = data['onedrive_link_logs']
    log_id = mongo_service.create_log_entry(run_id, onedrive_link_logs, onedrive_link_results)
    return jsonify({'message': 'Log created', 'log_id': str(log_id)}), 201

@app.route('/logs/<run_id>', methods=['GET'])
def retrieve_log(run_id):
    log_entry = mongo_service.get_log_entry(run_id)
    if log_entry:
        log_entry.pop('_id', None)  
        return jsonify(log_entry)
    else:
        return jsonify({'message': 'Log not found'}), 404

@app.route('/logs/<run_id>', methods=['PUT'])
def update_log(run_id):
    data = request.json
    onedrive_link_logs = data['onedrive_link_logs']
    onedrive_link_results = data['onedrive_link_results']
    modified_count = mongo_service.update_log_entry(run_id, onedrive_link_logs, onedrive_link_results)
    if modified_count:
        return jsonify({'message': 'Log updated'}), 200
    else:
        return jsonify({'message': 'Update failed'}), 404

@app.route('/logs/<run_id>', methods=['DELETE'])
def delete_log(run_id):
    deleted_count = mongo_service.delete_log_entry(run_id)
    if deleted_count:
        return jsonify({'message': 'Log deleted'}), 200
    else:
        return jsonify({'message': 'Delete failed'}), 404

if __name__ == "__main__":
    app.run(debug=True, port=8000)