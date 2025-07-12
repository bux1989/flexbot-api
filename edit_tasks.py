# edit_tasks.py
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

# Now you can use the Blueprint's route decorator
@edit_tasks_bp.route("/edit-task", methods=["PATCH"])
def edit_task():
    """
    Endpoint to edit a task's title and labels.
    Expects JSON payload with `task_id`, `title`, and `labels`.
    """
    data = request.get_json()
    print(data)  # Log the incoming request data

    task_id = data.get("task_id")
    title = data.get("title")
    labels = data.get("labels")

    if not task_id:
        return jsonify({"error": "task_id is required"}), 400

    try:
        task = api.update_task(
            task_id=task_id,
            labels=labels,  # Add labels if provided
            content=title  # Update title if provided
        )
        return jsonify({"message": "Task updated successfully", "task": task}), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500
