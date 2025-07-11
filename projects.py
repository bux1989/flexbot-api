from flask import Blueprint, request, jsonify
from utils import get_headers
from cache import cache_get, cache_set
import requests

projects_bp = Blueprint('projects', __name__)

def get_api_key():
    api_key = request.headers.get("X-Todoist-Api-Key")
    if not api_key:
        data = request.get_json(silent=True) or {}
        api_key = data.get("api_key")
    return api_key

@projects_bp.route("/list-projects", methods=["GET"])
def list_projects():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    cache_key = f"projects_{api_key}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify(cached)
    resp = requests.get("https://api.todoist.com/rest/v2/projects", headers=get_headers(api_key))
    try:
        data = resp.json()
    except Exception:
        return jsonify({"error": "Invalid response from Todoist", "details": resp.text}), resp.status_code
    cache_set(cache_key, data, ttl=60)  # Cache for 60 seconds
    return jsonify(data), resp.status_code

@projects_bp.route("/create-project", methods=["POST"])
def create_project():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    project_data = {
        "name": data.get("name"),
        "parent_id": data.get("parent_id"),
        "color": data.get("color")
    }
    project_data = {k: v for k, v in project_data.items() if v is not None}
    resp = requests.post("https://api.todoist.com/rest/v2/projects", json=project_data, headers=get_headers(api_key))
    try:
        return jsonify(resp.json()), resp.status_code
    except Exception:
        return jsonify({"error": "Invalid response from Todoist", "details": resp.text}), resp.status_code

@projects_bp.route("/edit-project", methods=["POST"])
def edit_project():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    project_id = data.get("project_id")
    if not project_id:
        return jsonify({"error": "project_id required"}), 400
    update_data = {
        "name": data.get("name"),
        "color": data.get("color")
    }
    update_data = {k: v for k, v in update_data.items() if v is not None}
    resp = requests.post(f"https://api.todoist.com/rest/v2/projects/{project_id}", json=update_data, headers=get_headers(api_key))
    try:
        return jsonify(resp.json()), resp.status_code
    except Exception:
        return jsonify({"error": "Invalid response from Todoist", "details": resp.text}), resp.status_code

@projects_bp.route("/delete-project", methods=["POST"])
def delete_project():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    project_id = data.get("project_id")
    if not project_id:
        return jsonify({"error": "project_id required"}), 400
    resp = requests.delete(f"https://api.todoist.com/rest/v2/projects/{project_id}", headers=get_headers(api_key))
    if resp.status_code == 204:
        return jsonify({"status": "deleted"}), 204
    else:
        return jsonify({"error": "Failed to delete project", "details": resp.text}), resp.status_code
