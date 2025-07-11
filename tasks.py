from flask import Blueprint, request, jsonify
from utils import HEADERS, get_all_tasks
import requests

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route("/create-task", methods=["POST"])
def create_task():
    data = request.get_json()
    task_data = {
        "content": data.get("title"),
        "priority": data.get("priority", 1),
        "due_string": data.get("due_string"),
        "project_id": data.get("project_id"),
        "section_id": data.get("section_id")
    }
    task_data = {k: v for k, v in task_data.items() if v}
    response = requests.post("https://api.todoist.com/rest/v2/tasks", json=task_data, headers=HEADERS)
    return jsonify(response.json()), response.status_code

@tasks_bp.route("/edit-task", methods=["POST"])
def edit_task():
    data = request.get_json()
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    task_data = {k: v for k, v in data.items() if k in {"title", "priority", "due_string"}}
    response = requests.post(f"https://api.todoist.com/rest/v2/tasks/{task_id}", json=task_data, headers=HEADERS)
    return jsonify(response.json()), response.status_code

@tasks_bp.route("/complete-task", methods=["POST"])
def complete_task():
    task_id = request.json.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    response = requests.post(f"https://api.todoist.com/rest/v2/tasks/{task_id}/close", headers=HEADERS)
    return jsonify({"status": "completed"}), response.status_code

@tasks_bp.route("/delete-task", methods=["POST"])
def delete_task():
    task_id = request.json.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    response = requests.delete(f"https://api.todoist.com/rest/v2/tasks/{task_id}", headers=HEADERS)
    return jsonify({"status": "deleted"}), response.status_code

@tasks_bp.route("/list-tasks", methods=["GET"])
def list_tasks():
    response = requests.get("https://api.todoist.com/rest/v2/tasks", headers=HEADERS)
    return jsonify(response.json()), response.status_code

@tasks_bp.route("/create-recurring-task", methods=["POST"])
def create_recurring_task():
    data = request.get_json()
    task_data = {
        "content": data.get("title"),
        "due_string": data.get("due_string"),
    }
    response = requests.post("https://api.todoist.com/rest/v2/tasks", json=task_data, headers=HEADERS)
    return jsonify(response.json()), response.status_code

@tasks_bp.route("/move-task", methods=["POST"])
def move_task():
    data = request.get_json()
    task_id = data.get("task_id")
    project_id = data.get("project_id")
    section_id = data.get("section_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    update_data = {}
    if project_id:
        update_data["project_id"] = project_id
    if section_id:
        update_data["section_id"] = section_id
    response = requests.post(f"https://api.todoist.com/rest/v2/tasks/{task_id}", json=update_data, headers=HEADERS)
    return jsonify(response.json()), response.status_code

@tasks_bp.route("/duplicate-task", methods=["POST"])
def duplicate_task():
    data = request.get_json()
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    orig_task_resp = requests.get(f"https://api.todoist.com/rest/v2/tasks/{task_id}", headers=HEADERS)
    if orig_task_resp.status_code != 200:
        return jsonify({"error": "Original task not found"}), 404
    orig_task = orig_task_resp.json()
    new_task = {k: orig_task.get(k) for k in ["content", "priority", "due_string", "project_id", "section_id"] if orig_task.get(k)}
    new_task["content"] = f"Copy of: {orig_task['content']}"
    resp = requests.post("https://api.todoist.com/rest/v2/tasks", json=new_task, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@tasks_bp.route("/bulk-edit-tasks", methods=["POST"])
def bulk_edit_tasks():
    data = request.get_json()
    task_ids = data.get("task_ids", [])
    update_fields = data.get("fields", {})
    results = []
    for task_id in task_ids:
        resp = requests.post(f"https://api.todoist.com/rest/v2/tasks/{task_id}", json=update_fields, headers=HEADERS)
        results.append({"task_id": task_id, "result": resp.json(), "status": resp.status_code})
    return jsonify(results)
