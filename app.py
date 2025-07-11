from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")
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
        "reminder": data.get("reminder")
    }

    # Clean up empty fields
    task_data = {k: v for k, v in task_data.items() if v}

    response = requests.post("https://api.todoist.com/rest/v2/tasks", json=task_data, headers=HEADERS)
    return jsonify(response.json()), response.status_code

@app.route("/create-project", methods=["POST"])
def create_project():
    data = request.get_json()
    response = requests.post("https://api.todoist.com/rest/v2/projects", json={"name": data.get("name")}, headers=HEADERS)
    return jsonify(response.json()), response.status_code

@app.route("/add-reminder", methods=["POST"])
def add_reminder():
    data = request.get_json()
    reminder = {
        "task_id": data.get("task_id"),
        "due_datetime": data.get("due_datetime"),  # ISO format
        "service": "email"  # or "push"
    }
    response = requests.post("https://api.todoist.com/rest/v2/reminders", json=reminder, headers=HEADERS)
    return jsonify(response.json()), response.status_code

@app.route("/auto-prioritize", methods=["POST"])
def auto_prioritize():
    data = request.get_json()
    task_title = data.get("title", "").lower()
    priority = 1
    if any(word in task_title for word in ["urgent", "asap", "today"]):
        priority = 4
    elif any(word in task_title for word in ["soon", "important"]):
        priority = 3
    elif "" == task_title.strip():
        priority = 1
    else:
        priority = 2
    return jsonify({"priority": priority})

@app.route("/smart-filter", methods=["GET"])
def smart_filter():
    filter_type = request.args.get("filter")
    all_tasks = get_all_tasks()
    today = datetime.utcnow().date()
    filtered = []
    for task in all_tasks:
        due = task.get("due", {}).get("date")
        if due:
            due_date = datetime.fromisoformat(due).date()
            if filter_type == "this_week" and (0 <= (due_date - today).days < 7):
                filtered.append(task)
    return jsonify(filtered)

@app.route("/archive-completed", methods=["POST"])
def archive_completed():
    # Just a placeholder - Todoist auto-archives completed tasks
    return jsonify({"status": "Todoist handles archiving automatically."})

@app.route("/weekly-summary", methods=["GET"])
def weekly_summary():
    week_ago = (datetime.utcnow() - timedelta(days=7)).date().isoformat()
    completed = get_completed_tasks()
    summary = [t for t in completed.get("items", []) if t.get("completed_date", "").split("T")[0] >= week_ago]
    return jsonify(summary)

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

# ---------------------------------------------
# Health Check
# ---------------------------------------------

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "FlexBot Todoist API running."})

# ---------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
