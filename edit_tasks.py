from flask import Blueprint, request, jsonify
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the Todoist API with key from .env
api = TodoistAPI(os.getenv("TODOIST_API_KEY"))

# Create a Blueprint for task editing -- THIS MUST BE DEFINED BEFORE ROUTES
edit_tasks_bp = Blueprint('edit_tasks', __name__)

@edit_tasks_bp.route("/edit-task", methods=["PATCH"])
def edit_task():
    print("Received PATCH request to /edit-task")

    # Get JSON payload
    data = request.get_json()
    print(f"Raw request.get_json(): {data}")

    if not data:
        print("Error: No data provided in request body")
        return jsonify({"error": "No data provided"}), 400

    # Extract and log individual fields
    task_id = data.get("task_id")
    print(f"Extracted task_id: {task_id}")

    title = data.get("title")
    print(f"Extracted title: {title}")

    labels = data.get("labels")
    print(f"Extracted labels: {labels}")

    # Validation
    if not task_id:
        print("Error: task_id is required but not provided")
        return jsonify({"error": "task_id is required"}), 400
    if not title:
        print("Error: title is required but not provided")
        return jsonify({"error": "title is required"}), 400

    try:
        # Prepare update arguments
        kwargs = {'task_id': task_id, 'content': title}
        print(f"Prepared kwargs for update_task: {kwargs}")

        if labels is not None:  # Allow empty list, don't skip if labels == []
            kwargs['labels'] = labels
            print(f"Added labels to kwargs: {labels}")

        print(f"Calling api.update_task with: {kwargs}")
        task = api.update_task(**kwargs)
        print(f"api.update_task returned: {task}")

        # Try serializing task
        try:
            if hasattr(task, 'to_dict'):
                task_dict = task.to_dict()
                print("Converted task to dict using to_dict()")
            else:
                task_dict = vars(task)
                print("Converted task to dict using vars()")
        except Exception as ser_error:
            print(f"Error serializing task object: {ser_error}")
            task_dict = str(task)

        print("Task updated successfully.")
        return jsonify({"message": "Task updated successfully", "task": task_dict}), 200

    except Exception as error:
        print("Exception occurred during task update.")
        print(f"Type of error: {type(error)}")
        print(f"Error updating task: {str(error)}")
        import traceback
        traceback.print_exc()  # Print the full traceback for debugging

        return jsonify({"error": str(error)}), 500
