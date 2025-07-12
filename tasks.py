from flask import Blueprint, request, jsonify
from utils import get_headers
from cache import cache_get, cache_set
import requests

tasks_bp = Blueprint('tasks', __name__)

def safe_json_response(response):
    """Safely handle empty or invalid JSON responses."""
    if response.content:
        try:
            return jsonify(response.json()), response.status_code
        except Exception:
            return jsonify({"message": response.text or "No response content", "status_code": response.status_code}), response.status_code
    else:
        return jsonify({"message": "No response content", "status_code": response.status_code}), response.status_code

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
    response = requests.post("https://api.todoist.com/rest/v2/tasks", json=task_data, headers=get_headers())
    return safe_json_response(response)

@tasks_bp.route("/edit-task", methods=["POST"])
def edit_task():
    data = request.get_json()
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400

    valid_fields = {
        "title": "content",
        "priority": "priority",
        "due_string": "due_string",
        "labels": "label_ids"  # ✅ Add this line
    }

    update_data = {
        api_field: data[field]
        for field, api_field in valid_fields.items()
        if data.get(field) is not None
    }

    if not update_data:
        return jsonify({"error": "At least one updatable field required (title, priority, due_string, labels)"}), 400

    response = requests.post(
        f"https://api.todoist.com/rest/v2/tasks/{task_id}",
        json=update_data,
        headers=get_headers()
    )
    return safe_json_response(response)

@tasks_bp.route("/complete-task", methods=["POST"])
def complete_task():
    data = request.get_json()
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    response = requests.post(f"https://api.todoist.com/rest/v2/tasks/{task_id}/close", headers=get_headers())
    return safe_json_response(response)

@tasks_bp.route("/delete-task", methods=["POST"])
def delete_task():
    data = request.get_json()
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    response = requests.delete(f"https://api.todoist.com/rest/v2/tasks/{task_id}", headers=get_headers())
    return safe_json_response(response)

@tasks_bp.route("/list-tasks", methods=["GET"])
def list_tasks():
    cache_key = "tasks"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)
    response = requests.get("https://api.todoist.com/rest/v2/tasks", headers=get_headers())
    data = response.json()
    cache_set(cache_key, data, ttl=60)
    return jsonify(data), response.status_code

@tasks_bp.route("/create-recurring-task", methods=["POST"])
def create_recurring_task():
    data = request.get_json()
    task_data = {
        "content": data.get("title"),
        "due_string": data.get("due_string"),
    }
    response = requests.post("https://api.todoist.com/rest/v2/tasks", json=task_data, headers=get_headers())
    return safe_json_response(response)

@tasks_bp.route("/move-task", methods=["POST"])
def move_task():
    data = request.get_json()
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400

    update_data = {}
    for field in ["project_id", "section_id", "parent_id"]:
        if data.get(field) is not None:
            update_data[field] = data[field]

    if not update_data:
        return jsonify({"error": "At least one of project_id, section_id, or parent_id must be provided"}), 400

    # Attempt official move
    move_resp = requests.post(
        f"https://api.todoist.com/rest/v2/tasks/{task_id}/move",
        json=update_data,
        headers=get_headers()
    )

    if move_resp.status_code == 200:
        return safe_json_response(move_resp)

    elif move_resp.status_code == 404:
        print("Move failed with 404 — attempting fallback (duplicate + delete)")

        # Fallback: duplicate and delete
        orig_resp = requests.get(f"https://api.todoist.com/rest/v2/tasks/{task_id}", headers=get_headers())
        if orig_resp.status_code != 200:
            return jsonify({"error": "Original task not found for duplication fallback"}), 404

        orig_task = orig_resp.json()
        print(f"Original task: {orig_task}")

        due = orig_task.get("due") or {}

        new_task = {
            "content": orig_task.get("content"),
            "priority": orig_task.get("priority"),
            "due_string": due.get("string"),
            "project_id": update_data.get("project_id", orig_task.get("project_id")),
            "section_id": update_data.get("section_id", orig_task.get("section_id"))
        }
        new_task = {k: v for k, v in new_task.items() if v}
        print(f"New task payload: {new_task}")

        create_resp = requests.post("https://api.todoist.com/rest/v2/tasks", json=new_task, headers=get_headers())
        if create_resp.status_code == 200:
            delete_resp = requests.delete(f"https://api.todoist.com/rest/v2/tasks/{task_id}", headers=get_headers())
            return jsonify({
                "message": "Fallback move completed via duplicate + delete",
                "new_task": create_resp.json()
            }), 200
        else:
            return jsonify({"error": "Fallback duplication failed", "details": create_resp.text}), create_resp.status_code

    else:
        return safe_json_response(move_resp)

@tasks_bp.route("/duplicate-task", methods=["POST"])
def duplicate_task():
    data = request.get_json()
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400

    orig_task_resp = requests.get(f"https://api.todoist.com/rest/v2/tasks/{task_id}", headers=get_headers())
    if orig_task_resp.status_code != 200:
        return jsonify({"error": "Original task not found"}), 404
    orig_task = orig_task_resp.json()
    new_task = {k: orig_task.get(k) for k in ["content", "priority", "due_string", "project_id", "section_id"] if orig_task.get(k)}
    new_task["content"] = f"Copy of: {orig_task['content']}"
    resp = requests.post("https://api.todoist.com/rest/v2/tasks", json=new_task, headers=get_headers())
    return safe_json_response(resp)

@tasks_bp.route("/bulk-edit-tasks", methods=["POST"])
def bulk_edit_tasks():
    data = request.get_json()
    task_ids = data.get("task_ids", [])
    update_fields = data.get("fields", {})

    valid_fields = {
        "title": "content", "description": "description",
        "labels": "label_ids", "priority": "priority",
        "due_string": "due_string", "due_date": "due_date",
        "due_datetime": "due_datetime", "due_lang": "due_lang",
        "assignee_id": "assignee_id", "duration": "duration",
        "duration_unit": "duration_unit", "deadline_date": "deadline_date",
        "deadline_lang": "deadline_lang"
    }
    update_data = {
        v: update_fields[k]
        for k, v in valid_fields.items()
        if update_fields.get(k) is not None
    }
    if not update_data:
        return jsonify({"error": "No valid fields to update"}), 400

    results = []
    for task_id in task_ids:
        resp = requests.post(
            f"https://api.todoist.com/rest/v2/tasks/{task_id}",
            json=update_data,
            headers=get_headers()
        )
        result = None
        if resp.content:
            try:
                result = resp.json()
            except Exception:
                result = {"message": resp.text or "No response content"}
        results.append({
            "task_id": task_id,
            "result": result,
            "status": resp.status_code
        })
    return jsonify(results)

