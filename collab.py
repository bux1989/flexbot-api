from flask import Blueprint, request, jsonify
from utils import get_headers
import requests

collab_bp = Blueprint('collab', __name__)

@collab_bp.route("/assign-tasks-to-role", methods=["POST"])
def assign_tasks_to_role():
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
            headers=get_headers()  # <-- No api_key argument, always uses ENV
        )
        try:
            result = resp.json()
        except Exception:
            result = {"message": resp.text}
        results.append({"task_id": task_id, "status": resp.status_code, "result": result})
    return jsonify(results)

@collab_bp.route("/mention-alerts", methods=["POST"])
def mention_alerts():
    data = request.get_json()
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    if not task_id or not user_id:
        return jsonify({"error": "task_id and user_id required"}), 400
    comment_data = {
        "task_id": task_id,
        "content": f"<@{user_id}> You were mentioned in this task."
    }
    resp = requests.post(
        "https://api.todoist.com/rest/v2/comments",
        json=comment_data,
        headers=get_headers()
    )
    try:
        result = resp.json()
    except Exception:
        result = {"message": resp.text}
    return jsonify({"status": "mention sent", "result": result}), resp.status_code
