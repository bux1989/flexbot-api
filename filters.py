from flask import Blueprint, request, jsonify
from utils import get_headers
from cache import cache_get, cache_set, cache_clear  # <-- Import caching functions
import requests
from datetime import datetime, timedelta

filters_bp = Blueprint('filters', __name__)

def get_api_key():
    api_key = request.headers.get("X-Todoist-Api-Key")
    if not api_key:
        data = request.get_json(silent=True) or {}
        api_key = data.get("api_key")
    return api_key

@filters_bp.route("/get-tasks-by-filter", methods=["POST"])
def get_tasks_by_filter():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    filter_type = data.get("filter")

    # Add caching (cache is per user and per filter)
    cache_key = f"filtered_tasks_{api_key}_{filter_type}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)

    resp = requests.get("https://api.todoist.com/rest/v2/tasks", headers=get_headers(api_key))
    all_tasks = resp.json()
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

    cache_set(cache_key, filtered, ttl=60)  # Cache result for 60 seconds
    return jsonify(filtered)

@filters_bp.route("/reschedule-by-label", methods=["POST"])
def reschedule_by_label():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    label = data.get("label")
    new_due = data.get("due_string")
    if not label or not new_due:
        return jsonify({"error": "label and due_string required"}), 400
    resp = requests.get("https://api.todoist.com/rest/v2/tasks", headers=get_headers(api_key))
    tasks = resp.json()
    updated = []
    for task in tasks:
        if label in [lbl.lower() for lbl in task.get("labels", [])]:
            task_id = task["id"]
            patch_data = {"due_string": new_due}
            edit_resp = requests.post(f"https://api.todoist.com/rest/v2/tasks/{task_id}", json=patch_data, headers=get_headers(api_key))
            updated.append({"task_id": task_id, "status": edit_resp.status_code})
    return jsonify(updated)

@filters_bp.route("/rollover-overdue", methods=["POST"])
def rollover_overdue():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    resp = requests.get("https://api.todoist.com/rest/v2/tasks", headers=get_headers(api_key))
    tasks = resp.json()
    today = datetime.utcnow().date()
    updated = []
    for task in tasks:
        due = task.get("due", {}).get("date")
        try:
            due_date = datetime.fromisoformat(due).date()
        except Exception:
            continue
        if due_date and due_date < today:
            patch_data = {"due_string": "today"}
            edit_resp = requests.post(f"https://api.todoist.com/rest/v2/tasks/{task['id']}", json=patch_data, headers=get_headers(api_key))
            updated.append({"task_id": task["id"], "status": edit_resp.status_code})
    return jsonify(updated)

@filters_bp.route("/archive-completed", methods=["POST"])
def archive_completed():
    # Todoist handles archiving automatically; nothing to do.
    return jsonify({"status": "Todoist handles archiving automatically."})

@filters_bp.route("/weekly-summary", methods=["GET"])
def weekly_summary():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    week_ago = (datetime.utcnow() - timedelta(days=7)).date().isoformat()
    resp = requests.get("https://api.todoist.com/sync/v9/completed/get_all", headers=get_headers(api_key))
    completed = resp.json()
    summary = [t for t in completed.get("items", []) if t.get("completed_date", "").split("T")[0] >= week_ago]
    return jsonify(summary)

@filters_bp.route("/flush-cache", methods=["GET"])
def flush_cache():
    cache_clear()
    return jsonify({"status": "cache flushed"})
