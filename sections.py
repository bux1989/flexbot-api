from flask import Blueprint, request, jsonify
from utils import get_headers
import requests

sections_bp = Blueprint('sections', __name__)

def get_api_key():
    api_key = request.headers.get("X-Todoist-Api-Key")
    if not api_key:
        data = request.get_json(silent=True) or {}
        api_key = data.get("api_key")
    return api_key

def safe_json_response(response):
    if response.content:
        try:
            return jsonify(response.json()), response.status_code
        except Exception:
            return jsonify({"message": response.text or "No response content", "status_code": response.status_code}), response.status_code
    else:
        return jsonify({"message": "No response content", "status_code": response.status_code}), response.status_code

@sections_bp.route("/create-section", methods=["POST"])
def create_section():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    section_data = {
        "name": data.get("name"),
        "project_id": data.get("project_id")
    }
    if not section_data["name"] or not section_data["project_id"]:
        return jsonify({"error": "Both name and project_id are required"}), 400
    resp = requests.post("https://api.todoist.com/rest/v2/sections", json=section_data, headers=get_headers(api_key))
    return safe_json_response(resp)

@sections_bp.route("/edit-section", methods=["POST"])
def edit_section():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    section_id = data.get("section_id")
    new_name = data.get("name")
    if not section_id:
        return jsonify({"error": "section_id required"}), 400
    if not new_name:
        return jsonify({"error": "name is required to update a section"}), 400
    update_data = {"name": new_name}
    resp = requests.post(f"https://api.todoist.com/rest/v2/sections/{section_id}", json=update_data, headers=get_headers(api_key))
    return safe_json_response(resp)

@sections_bp.route("/delete-section", methods=["POST"])
def delete_section():
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    data = request.get_json()
    section_id = data.get("section_id")
    if not section_id:
        return jsonify({"error": "section_id required"}), 400
    resp = requests.delete(f"https://api.todoist.com/rest/v2/sections/{section_id}", headers=get_headers(api_key))
    return jsonify({"status": "deleted"}), resp.status_code
