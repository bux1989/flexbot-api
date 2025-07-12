from flask import Blueprint, request, jsonify
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the Todoist API
api = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))

# Create a Blueprint for task editing
edit_tasks_bp = Blueprint('edit_tasks', __name__)

@edit_tasks_bp.route("/edit-task", methods=["PATCH"])
def edit_task():
    """
    Endpoint to edit a task's title and labels.
    Expects JSON payload with `task_id`, `title`, and `labels`.
    """
    # Log incoming request data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    print(f"Received data: {data}")  # Log the incoming request data for debugging

    task_id = data.get("task_id")
    title = data.get("title")
    labels = data.get("labels")

    # Validate that required fields are provided
    if not task_id:
        return jsonify({"error": "task_id is required"}), 400
    if not title:
        return jsonify({"error": "title is required"}), 400

    # Try to update the task
    try:
        task = api.update_task(
            task_id=task_id,
            labels=labels,  # Add labels if provided
            content=title  # Update title if provided
        )
        return jsonify({"message": "Task updated successfully", "task": task}), 200

    except Exception as error:
        print(f"Error updating task: {str(error)}")  # Log error for debugging
        return jsonify({"error": str(error)}), 500
