from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Get your Todoist API key from environment variable
TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "✅ FlexBot API is live!"

@app.route("/create-task", methods=["POST"])
def create_task():
    data = request.get_json()

    title = data.get("title")
    priority = data.get("priority", 1)
    project_id = data.get("project_id")  # Optional
    section_id = data.get("section_id")  # Optional

    if not title:
        return jsonify({"error": "Missing task title"}), 400

    task_data = {
        "content": title,
        "priority": priority
    }

    if project_id:
        task_data["project_id"] = project_id
    if section_id:
        task_data["section_id"] = section_id

    headers = {
        "Authorization": f"Bearer {TODOIST_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.todoist.com/rest/v2/tasks",
        json=task_data,
        headers=headers
    )

    if response.status_code != 200 and response.status_code != 204:
        return jsonify({"error": "Failed to create task", "details": response.text}), response.status_code

    return jsonify({"status": "success", "todoist_response": response.json()}), 200
