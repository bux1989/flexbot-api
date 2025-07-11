from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")

# Headers for all Todoist requests
HEADERS = {
    "Authorization": f"Bearer {TODOIST_API_KEY}",
    "Content-Type": "application/json"
}

# Create a task
@app.route("/create-task", methods=["POST"])
def create_task():
    data = request.get_json()
    task_data = {
        "content": data.get("title"),
        "priority": data.get("priority", 1),
        "due_string": data.get("due_string"),  # e.g., "tomorrow at 5pm"
        "project_id": data.get("project_id"),
        "section_id": data.get("section_id"),
    }
    response = requests.post("https://api.todoist.com/rest/v2/tasks", json=task_data, headers=HEADERS)
    return jsonify(response.json()), response.status_code

# Edit a task
@app.route("/edit-task", methods=["POST"])
def edit_task():
    data = request.get_json()
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id is required"}), 400
    update_data = {
        "content": data.get("title"),
        "priority": data.get("priority"),
        "due_string": data.get("due_string")
    }
    response = requests.post(
        f"https://api.todoist.com/rest/v2/tasks/{task_id}",
        json={k: v for k, v in update_data.items() if v is not None},
        headers=HEADERS
    )
    return jsonify({"status": "Task updated"}), response.status_code

# Complete a task
@app.route("/complete-task", methods=["POST"])
def complete_task():
    data = request.get_json()
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id is required"}), 400
    response = requests.post(
        f"https://api.todoist.com/rest/v2/tasks/{task_id}/close",
        headers=HEADERS
    )
    return jsonify({"status": "Task completed"}), response.status_code

# Delete a task
@app.route("/delete-task", methods=["POST"])
def delete_task():
    data = request.get_json()
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id is required"}), 400
    response = requests.delete(
        f"https://api.todoist.com/rest/v2/tasks/{task_id}",
        headers=HEADERS
    )
    return jsonify({"status": "Task deleted"}), response.status_code

# List all active tasks
@app.route("/list-tasks", methods=["GET"])
def list_tasks():
    response = requests.get("https://api.todoist.com/rest/v2/tasks", headers=HEADERS)
    return jsonify(response.json()), response.status_code

# Create a section
@app.route("/create-section", methods=["POST"])
def create_section():
    data = request.get_json()
    section_data = {
        "name": data.get("name"),
        "project_id": data.get("project_id")
    }
    response = requests.post("https://api.todoist.com/rest/v2/sections", json=section_data, headers=HEADERS)
    return jsonify(response.json()), response.status_code

# Edit a section
@app.route("/edit-section", methods=["POST"])
def edit_section():
    data = request.get_json()
    section_id = data.get("section_id")
    if not section_id:
        return jsonify({"error": "section_id is required"}), 400
    response = requests.post(
        f"https://api.todoist.com/rest/v2/sections/{section_id}",
        json={"name": data.get("name")},
        headers=HEADERS
    )
    return jsonify({"status": "Section renamed"}), response.status_code

# Delete a section
@app.route("/delete-section", methods=["POST"])
def delete_section():
    data = request.get_json()
    section_id = data.get("section_id")
    if not section_id:
        return jsonify({"error": "section_id is required"}), 400
    response = requests.delete(
        f"https://api.todoist.com/rest/v2/sections/{section_id}",
        headers=HEADERS
    )
    return jsonify({"status": "Section deleted"}), response.status_code

if __name__ == "__main__":
    app.run(debug=True)
