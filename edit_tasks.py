from flask import Blueprint, request, jsonify
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

api = TodoistAPI(os.getenv("TODOIST_API_KEY"))
edit_tasks_bp = Blueprint('edit_tasks', __name__)

@edit_tasks_bp.route("/edit-task", methods=["PATCH"])
def edit_task():
    print("Received PATCH request to /edit-task")
    data = request.get_json()
    print(f"Raw request.get_json(): {data}")

    if not data:
        return jsonify({"error": "No data provided"}), 400

    task_id = data.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id is required"}), 400

    # Optional task fields
    title = data.get("title")
    description = data.get("description")
    labels = data.get("labels")
    priority = data.get("priority")
    due_string = data.get("due_string")
    due_lang = data.get("due_lang")
    due_date = data.get("due_date")
    due_datetime = data.get("due_datetime")
    assignee_id = data.get("assignee_id")
    day_order = data.get("day_order")
    collapsed = data.get("collapsed")
    duration = data.get("duration")
    duration_unit = data.get("duration_unit")
    deadline_date = data.get("deadline_date")
    deadline_lang = data.get("deadline_lang")

    # New: comment and reminder
    comment = data.get("comment")
    reminder_time = data.get("reminder_time")  # e.g. "2025-07-15T09:00:00Z"

    try:
        # Prepare update arguments (only if not None)
        kwargs = {'task_id': task_id}
        if title is not None:
            kwargs['content'] = title
        if description is not None:
            kwargs['description'] = description
        if labels is not None:
            kwargs['labels'] = labels
        if priority is not None:
            kwargs['priority'] = priority
        if due_string is not None:
            kwargs['due_string'] = due_string
        if due_lang is not None:
            kwargs['due_lang'] = due_lang
        if due_date is not None:
            kwargs['due_date'] = due_date
        if due_datetime is not None:
            kwargs['due_datetime'] = due_datetime
        if assignee_id is not None:
            kwargs['assignee_id'] = assignee_id
        if day_order is not None:
            kwargs['day_order'] = day_order
        if collapsed is not None:
            kwargs['collapsed'] = collapsed
        if duration is not None:
            kwargs['duration'] = duration
        if duration_unit is not None:
            kwargs['duration_unit'] = duration_unit
        if deadline_date is not None:
            kwargs['deadline_date'] = deadline_date
        if deadline_lang is not None:
            kwargs['deadline_lang'] = deadline_lang

        print(f"Calling api.update_task with: {kwargs}")
        task = api.update_task(**kwargs)
        print(f"api.update_task returned: {task}")

        responses = {"task": task.to_dict() if hasattr(task, 'to_dict') else vars(task)}

        # Add a comment if requested
        if comment:
            print(f"Adding comment: {comment}")
            comment_obj = api.add_comment(task_id=task_id, content=comment)
            responses["comment"] = comment_obj.to_dict() if hasattr(comment_obj, 'to_dict') else vars(comment_obj)

        # Add a reminder if requested
        if reminder_time:
            print(f"Adding reminder at: {reminder_time}")
            reminder_obj = api.add_reminder(task_id=task_id, due_datetime=reminder_time)
            responses["reminder"] = reminder_obj.to_dict() if hasattr(reminder_obj, 'to_dict') else vars(reminder_obj)

        print("Task updated successfully.")
        return jsonify({"message": "Task updated successfully", **responses}), 200

    except Exception as error:
        print("Exception occurred during task update.")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(error)}), 500
