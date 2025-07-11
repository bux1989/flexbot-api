...
@app.route("/assign-labels", methods=["POST"])
def assign_labels():
    import uuid
    data = request.get_json()
    task_id = data.get("task_id")
    label_ids = data.get("label_ids")  # List of label IDs

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

    headers = {
        "Authorization": f"Bearer {TODOIST_API_KEY}",
        "Content-Type": "application/json"
    }

    resp = requests.post("https://api.todoist.com/sync/v9/sync", json=payload, headers=headers)
    if resp.status_code != 200:
        return jsonify({"error": "Failed to assign labels", "details": resp.text}), resp.status_code

    return jsonify({"status": "Labels assigned", "response": resp.json()}), 200

...
