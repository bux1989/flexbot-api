from flask import Blueprint, request, jsonify
from utils import get_headers
import requests
import uuid

labels_bp = Blueprint('labels', __name__)

def safe_json_response(response):
    if response.content:
        try:
            return jsonify(response.json()), response.status_code
        except Exception:
            return jsonify({"error": "Invalid response from Todoist", "details": response.text}), response.status_code
    else:
        return jsonify({"message": "No response content", "status_code": response.status_code}), response.status_code

@labels_bp.route("/list-labels", methods=["GET"])
def list_labels():
    resp = requests.get("https://api.todoist.com/rest/v2/labels", headers=get_headers())
    return safe_json_response(resp)

@labels_bp.route("/create-label", methods=["POST"])
def create_label():
    data = request.get_json()
    label_data = {
        "name": data.get("name"),
        "color": data.get("color"),
        "favorite": data.get("favorite", False)
    }
    label_data = {k: v for k, v in label_data.items() if v is not None}
    resp = requests.post("https://api.todoist.com/rest/v2/labels", json=label_data, headers=get_headers())
    return safe_json_response(resp)

@labels_bp.route("/edit-label", methods=["POST"])
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
    resp = requests.post(f"https://api.todoist.com/rest/v2/labels/{label_id}", json=update_data, headers=get_headers())
    return safe_json_response(resp)

@labels_bp.route("/delete-label", methods=["POST"])
def delete_label():
    data = request.get_json()
    label_id = data.get("label_id")
    if not label_id:
        return jsonify({"error": "label_id required"}), 400
    resp = requests.delete(f"https://api.todoist.com/rest/v2/labels/{label_id}", headers=get_headers())
    if resp.status_code == 204:
        return jsonify({"status": "deleted"}), 204
    else:
        return jsonify({"error": "Failed to delete label", "details": resp.text}), resp.status_code

@labels_bp.route("/assign-labels", methods=["POST"])
def assign_labels():
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
    resp = requests.post("https://api.todoist.com/sync/v9/sync", json=payload, headers=get_headers())
    return safe_json_response(resp)
