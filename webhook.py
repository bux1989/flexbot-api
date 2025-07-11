from flask import Blueprint, request, jsonify
from cache import cache_clear  # Or use fine-grained invalidation if you add it

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/todoist-webhook', methods=['POST'])
def todoist_webhook():
    event = request.get_json()
    print("Received webhook event:", event)  # You might want to log this in production

    # EXAMPLE: Invalidate cache if a task is added, updated, or deleted
    event_type = event.get("event_name")
    user_id = event.get("initiator", {}).get("id")  # If available

    if event_type in ["task:added", "task:updated", "task:deleted"]:
        # Invalidate all cache (simple solution)
        cache_clear()
        print("Cache cleared due to task event.")

    # Optionally, add more logic for different event types

    return jsonify({"status": "received"}), 200
