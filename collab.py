from flask import Blueprint, request, jsonify
from utils import get_headers
import requests

collab_bp = Blueprint('collab', __name__)

def get_api_key():
    api_key = request.headers.get("X-Todoist-Api-Key")
    if not api_key:
        data = request.get_json(silent=True) or {}
        api_key = data.get("api_key")
    return api_key

@collab_bp.route("/assign-tasks-to-role", methods=["POST"])
def assign_tasks_to_role():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    # This is a stub – expand as needed for your actual role logic!
    data = request.get_json()
    task_ids = data.get("task_ids")
    role = data.get("role")
    assignee_id = data.get("assignee_id")
    if not task_ids or not role or not assignee_id:
        return jsonify({"error": "task_ids, role, and assignee_id required"}), 400
    results = []
    for task_id in task_ids:
        resp = requests.post(
            f"https://api.todoist.com/rest/v2/tasks/{task_id}",
            json={"responsible_uid": assignee_id},
            headers=get_headers(api_key)
        )
        results.append({"task_id": task_id, "status": resp.status_code})
    return jsonify(results)

@collab_bp.route("/mention-alerts", methods=["POST"])
def mention_alerts():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    if not task_id or not user_id:
        return jsonify({"error": "task_id and user_id required"}), 400
    # This is a stub – in reality, you might post a comment mentioning the user
    comment_data = {
        "task_id": task_id,
        "content": f"<@{user_id}> You were mentioned in this task."
    }
    resp = requests.post(
        "https://api.todoist.com/rest/v2/comments",
        json=comment_data,
        headers=get_headers(api_key)
    )
    return jsonify({"status": "mention sent", "result": resp.json()}), resp.status_code
