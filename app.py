from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")
if not TODOIST_API_KEY:
    raise ValueError("TODOIST_API_KEY environment variable not set.")

HEADERS = {
    "Authorization": f"Bearer {TODOIST_API_KEY}",
    "Content-Type": "application/json"
}

# ---------------------------------------------
# Helper Functions
# ---------------------------------------------
def get_all_tasks():
    resp = requests.get("https://api.todoist.com/rest/v2/tasks", headers=HEADERS)
    return resp.json()

def get_completed_tasks():
    resp = requests.get("https://api.todoist.com/sync/v9/completed/get_all", headers=HEADERS)
    return resp.json()

# ---------------------------------------------
# ROUTES
# ---------------------------------------------

@app.route("/create-task", methods=["POST"])
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

@app.route("/edit-task", methods=["POST"])
def edit_task():
    data = request.get_json()
    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    task_data = {k: v for k, v in data.items() if k in {"title", "priority", "due_string"}}
    response = requests.post(f"https://api.todoist.com/rest/v2/tasks/{task_id}", json=task_data, headers=HEADERS)
    return jsonify(response.json()), response.status_code

@app.route("/complete-task", methods=["POST"])
def complete_task():
    task_id = request.json.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    response = requests.post(f"https://api.todoist.com/rest/v2/tasks/{task_id}/close", headers=HEADERS)
    return jsonify({"status": "completed"}), response.status_code

@app.route("/delete-task", methods=["POST"])
def delete_task():
    task_id = request.json.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    response = requests.delete(f"https://api.todoist.com/rest/v2/tasks/{task_id}", headers=HEADERS)
    return jsonify({"status": "deleted"}), response.status_code

@app.route("/list-tasks", methods=["GET"])
def list_tasks():
    response = requests.get("https://api.todoist.com/rest/v2/tasks", headers=HEADERS)
    return jsonify(response.json()), response.status_code

@app.route("/create-recurring-task", methods=["POST"])
def create_recurring_task():
    data = request.get_json()
    task_data = {
        "content": data.get("title"),
        "due_string": data.get("due_string"),
    }
    response = requests.post("https://api.todoist.com/rest/v2/tasks", json=task_data, headers=HEADERS)
    return jsonify(response.json()), response.status_code

@app.route("/add-reminder", methods=["POST"])
def add_reminder():
    data = request.get_json()
    reminder = {
        "task_id": data.get("task_id"),
        "due_datetime": data.get("reminder_time"),
        "service": "email"
    }
    response = requests.post("https://api.todoist.com/rest/v2/reminders", json=reminder, headers=HEADERS)
    return jsonify(response.json()), response.status_code

@app.route("/get-tasks-by-filter", methods=["POST"])
def get_tasks_by_filter():
    data = request.get_json()
    filter_type = data.get("filter")
    all_tasks = get_all_tasks()
    today = datetime.utcnow().date()
    filtered = []
    for task in all_tasks:
        due = task.get("due", {}).get("date")
        try:
            due_date = datetime.fromisoformat(due).date()
        except Exception:
            continue
        if filter_type == "this_week" and (0 <= (due_date - today).days < 7):
            filtered.append(task)
    return jsonify(filtered)

@app.route("/auto-prioritize", methods=["POST"])
def auto_prioritize():
    data = request.get_json()
    task_title = data.get("title", "").lower()
    priority = 1
    if any(word in task_title for word in ["urgent", "asap", "today"]):
        priority = 4
    elif any(word in task_title for word in ["soon", "important"]):
        priority = 3
    elif task_title.strip() == "":
        priority = 1
    else:
        priority = 2
    return jsonify({"priority": priority})

@app.route("/smart-sort", methods=["POST"])
def smart_sort():
    data = request.get_json()
    task_title = data.get("title", "").lower()
    suggested_project = "Inbox"
    if "meeting" in task_title:
        suggested_project = "Work"
    elif "groceries" in task_title:
        suggested_project = "Personal"
    elif "invoice" in task_title:
        suggested_project = "Finance"
    return jsonify({"suggested_project": suggested_project})

@app.route("/archive-completed", methods=["POST"])
def archive_completed():
    return jsonify({"status": "Todoist handles archiving automatically."})

@app.route("/weekly-summary", methods=["GET"])
def weekly_summary():
    week_ago = (datetime.utcnow() - timedelta(days=7)).date().isoformat()
    completed = get_completed_tasks()
    summary = [t for t in completed.get("items", []) if t.get("completed_date", "").split("T")[0] >= week_ago]
    return jsonify(summary)

# -------------------- Labels --------------------

@app.route("/list-labels", methods=["GET"])
def list_labels():
    resp = requests.get("https://api.todoist.com/rest/v2/labels", headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/create-label", methods=["POST"])
def create_label():
    data = request.get_json()
    label_data = {
        "name": data.get("name"),
        "color": data.get("color"),
        "favorite": data.get("favorite", False)
    }
    label_data = {k: v for k, v in label_data.items() if v is not None}
    resp = requests.post("https://api.todoist.com/rest/v2/labels", json=label_data, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/edit-label", methods=["POST"])
def edit_label():
    data = request.get_json()
    label_id = data.get("label_id")
    if not label_id:
        return jsonify({"error": "label_id required"}), 400
    update_data = {
        "name": data.get("name"),
        "color": data.get("color"),
        "favorite": data.get("favorite")
    }
    update_data = {k: v for k, v in update_data.items() if v is not None}
    resp = requests.post(f"https://api.todoist.com/rest/v2/labels/{label_id}", json=update_data, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/delete-label", methods=["POST"])
def delete_label():
    label_id = request.get_json().get("label_id")
    if not label_id:
        return jsonify({"error": "label_id required"}), 400
    resp = requests.delete(f"https://api.todoist.com/rest/v2/labels/{label_id}", headers=HEADERS)
    return jsonify({"status": "deleted"}), resp.status_code

# -------------------- Projects --------------------

@app.route("/create-project", methods=["POST"])
def create_project():
    data = request.get_json()
    project_data = {
        "name": data.get("name"),
        "parent_id": data.get("parent_id"),
        "color": data.get("color")
    }
    project_data = {k: v for k, v in project_data.items() if v is not None}
    resp = requests.post("https://api.todoist.com/rest/v2/projects", json=project_data, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/edit-project", methods=["POST"])
def edit_project():
    data = request.get_json()
    project_id = data.get("project_id")
    if not project_id:
        return jsonify({"error": "project_id required"}), 400
    update_data = {
        "name": data.get("name"),
        "color": data.get("color")
    }
    update_data = {k: v for k, v in update_data.items() if v is not None}
    resp = requests.post(f"https://api.todoist.com/rest/v2/projects/{project_id}", json=update_data, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/delete-project", methods=["POST"])
def delete_project():
    project_id = request.get_json().get("project_id")
    if not project_id:
        return jsonify({"error": "project_id required"}), 400
    resp = requests.delete(f"https://api.todoist.com/rest/v2/projects/{project_id}", headers=HEADERS)
    return jsonify({"status": "deleted"}), resp.status_code

@app.route("/list-projects", methods=["GET"])
def list_projects():
    resp = requests.get("https://api.todoist.com/rest/v2/projects", headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

# -------------------- Sections --------------------

@app.route("/create-section", methods=["POST"])
def create_section():
    data = request.get_json()
    section_data = {
        "name": data.get("name"),
        "project_id": data.get("project_id")
    }
    resp = requests.post("https://api.todoist.com/rest/v2/sections", json=section_data, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/edit-section", methods=["POST"])
def edit_section():
    data = request.get_json()
    section_id = data.get("section_id")
    if not section_id:
        return jsonify({"error": "section_id required"}), 400
    update_data = {"name": data.get("name")}
    resp = requests.post(f"https://api.todoist.com/rest/v2/sections/{section_id}", json=update_data, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/delete-section", methods=["POST"])
def delete_section():
    section_id = request.get_json().get("section_id")
    if not section_id:
        return jsonify({"error": "section_id required"}), 400
    resp = requests.delete(f"https://api.todoist.com/rest/v2/sections/{section_id}", headers=HEADERS)
    return jsonify({"status": "deleted"}), resp.status_code

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "FlexBot Todoist API running."})

# ---------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
