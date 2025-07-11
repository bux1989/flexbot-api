from flask import Blueprint, request, jsonify
from utils import get_headers
import requests
import uuid

labels_bp = Blueprint('labels', __name__)

def get_api_key():
    api_key = request.headers.get("X-Todoist-Api-Key")
    if not api_key:
        data = request.get_json(silent=True) or {}
        api_key = data.get("api_key")
    return api_key

@labels_bp.route("/list-labels", methods=["GET"])
def list_labels():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    resp = requests.get("https://api.todoist.com/rest/v2/labels", headers=get_headers(api_key))
    try:
        return jsonify(resp.json()), resp.status_code
    except Exception:
        return jsonify({"error": "Invalid response from Todoist", "details": resp.text}), resp.status_code

@labels_bp.route("/create-label", methods=["POST"])
def create_label():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    label_data = {
        "name": data.get("name"),
        "color": data.get("color"),
        "favorite": data.get("favorite", False)
    }
    label_data = {k: v for k, v in label_data.items() if v is not None}
    resp = requests.post("https://api.todoist.com/rest/v2/labels", json=label_data, headers=get_headers(api_key))
    try:
        return jsonify(resp.json()), resp.status_code
    except Exception:
        return jsonify({"error": "Invalid response from Todoist", "details": resp.text}), resp.status_code

@labels_bp.route("/edit-label", methods=["POST"])
def edit_label():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
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
    resp = requests.post(f"https://api.todoist.com/rest/v2/labels/{label_id}", json=update_data, headers=get_headers(api_key))
    try:
        return jsonify(resp.json()), resp.status_code
    except Exception:
        return jsonify({"error": "Invalid response from Todoist", "details": resp.text}), resp.status_code

@labels_bp.route("/delete-label", methods=["POST"])
def delete_label():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    label_id = data.get("label_id")
    if not label_id:
        return jsonify({"error": "label_id required"}), 400
    resp = requests.delete(f"https://api.todoist.com/rest/v2/labels/{label_id}", headers=get_headers(api_key))
    if resp.status_code == 204:
        return jsonify({"status": "deleted"}), 204
    else:
        return jsonify({"error": "Failed to delete label", "details": resp.text}), resp.status_code

@labels_bp.route("/assign-labels", methods=["POST"])
def assign_labels():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    task_id = data.get("task_id")
    label_ids = data.get("label_ids")
    if not task_id or not isinstance(label_ids, list):
        return jsonify({"error": "task_id and label_ids (list) are required"}), 400
    payload = {
        "commands": [
            {
                "type": "item_update",
                "uuid": str(uuid.uuid4()),
                "args": {
                    "id": task_id,
                    "label_ids": label_ids
                }
            }
        ]
    }
    resp = requests.post("https://api.todoist.com/sync/v9/sync", json=payload, headers=get_headers(api_key))
    try:
        return jsonify({"status": "Labels assigned", "response": resp.json()}), resp.status_code
    except Exception:
        return jsonify({"error": "Failed to assign labels", "details": resp.text}), resp.status_code
