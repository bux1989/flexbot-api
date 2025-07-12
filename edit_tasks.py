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
    data = request.get_json()  # Parse the incoming request data
    print(data)  # Log for debugging

    # Get task details from the request body
    task_id = data.get("task_id")
    title = data.get("title")
    labels = data.get("labels")

    # Check if task_id is provided
    if not task_id:
        return jsonify({"error": "task_id is required"}), 400

    # Check if title is provided (optional: add more checks if needed)
    if not title:
        return jsonify({"error": "title is required"}), 400

    try:
        # Attempt to update the task using Todoist API
        task = api.update_task(
            task_id=task_id,
            labels=labels,  # Update labels if provided
            content=title  # Update title if provided
        )
        # Return success message and updated task data
        return jsonify({"message": "Task updated successfully", "task": task}), 200

    except Exception as error:
        # Handle exceptions and provide a relevant error message
        return jsonify({"error": str(error)}), 500
