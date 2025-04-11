from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

# Endpoint to receive data
@app.route('/submit-data', methods=['POST'])
def submit_data():
    data = request.json
    if not os.path.exists("results"):
        os.makedirs("results")
    filename = "results/memory_task_results.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as csvfile:
        fieldnames = [
            "name", "age", "gender", "start_time", "trial_index", "is_dual_task",
            "accuracy", "reaction_time", "high_tones_played", "high_tones_detected",
            "false_alarms", "avg_reaction_time"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for trial in data["trial_results"]:
            writer.writerow(trial)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)