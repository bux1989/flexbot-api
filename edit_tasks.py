@edit_tasks_bp.route("/edit-task", methods=["PATCH"])
def edit_task():
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
