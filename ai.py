from flask import Blueprint, request, jsonify
from utils import get_headers
import requests
from datetime import datetime, timedelta

ai_bp = Blueprint('ai', __name__)

def get_api_key():
    api_key = request.headers.get("X-Todoist-Api-Key")
    if not api_key:
        data = request.get_json(silent=True) or {}
        api_key = data.get("api_key")
    return api_key

@ai_bp.route("/auto-prioritize", methods=["POST"])
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

@ai_bp.route("/smart-sort", methods=["POST"])
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

@ai_bp.route("/assign-due-date-by-context", methods=["POST"])
def assign_due_date_by_context():
    data = request.get_json()
    context = data.get("context", "")
    if "urgent" in context.lower():
        due = "today"
    elif "next week" in context.lower():
        due = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")
    else:
        due = None
    return jsonify({"due_string": due})

@ai_bp.route("/suggest-labels-or-sections", methods=["POST"])
def suggest_labels_or_sections():
    data = request.get_json()
    title = data.get("title", "").lower()
    suggestions = {"labels": [], "sections": []}
    if "dev" in title:
        suggestions["labels"].append("Development")
    if "meeting" in title:
        suggestions["labels"].append("Meeting")
        suggestions["sections"].append("Meetings")
    if "urgent" in title:
        suggestions["labels"].append("Urgent")
    return jsonify(suggestions)

@ai_bp.route("/summarize-project", methods=["POST"])
def summarize_project():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    project_id = data.get("project_id")
    if not project_id:
        return jsonify({"error": "project_id required"}), 400
    tasks_resp = requests.get(f"https://api.todoist.com/rest/v2/tasks?project_id={project_id}", headers=get_headers(api_key))
    tasks = tasks_resp.json()
    summary = {
        "total": len(tasks),
        "completed": sum(1 for t in tasks if t.get("is_completed")),
        "remaining": sum(1 for t in tasks if not t.get("is_completed")),
        "tasks": [t.get("content") for t in tasks]
    }
    return jsonify(summary)

@ai_bp.route("/get-blocked-tasks", methods=["GET"])
def get_blocked_tasks():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    resp = requests.get("https://api.todoist.com/rest/v2/tasks", headers=get_headers(api_key))
    tasks = resp.json()
    blocked = [t for t in tasks if 'blocked' in [lbl.lower() for lbl in t.get('labels', [])]]
    return jsonify(blocked)
