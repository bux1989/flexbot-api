from flask import Blueprint, request, jsonify
from utils import HEADERS
import requests

projects_bp = Blueprint('projects', __name__)

@projects_bp.route("/list-projects", methods=["GET"])
def list_projects():
    resp = requests.get("https://api.todoist.com/rest/v2/projects", headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@projects_bp.route("/create-project", methods=["POST"])
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

@projects_bp.route("/edit-project", methods=["POST"])
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

@projects_bp.route("/delete-project", methods=["POST"])
def delete_project():
    project_id = request.get_json().get("project_id")
    if not project_id:
        return jsonify({"error": "project_id required"}), 400
    resp = requests.delete(f"https://api.todoist.com/rest/v2/projects/{project_id}", headers=HEADERS)
    return jsonify({"status": "deleted"}), resp.status_code
