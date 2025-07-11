from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")

@app.route("/create-task", methods=["POST"])
def create_task():
    data = request.get_json()
    title = data.get("title")
    priority = data.get("priority", 1)

    task_data = {
        "content": title,
        "priority": priority
    }

    headers = {
        "Authorization": f"Bearer {TODOIST_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.todoist.com/rest/v2/tasks",
        json=task_data,
        headers=headers
    )

    return jsonify(response.json()), response.status_code
