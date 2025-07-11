from flask import Blueprint, request, jsonify
from cache import cache_clear

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/todoist-webhook', methods=['POST'])
def todoist_webhook():
    event = request.get_json()
    print("Received webhook event:", event)

    event_type = event.get("event_name")
    user_id = event.get("initiator", {}).get("id")  # If available

    if event_type in ["item:added", "item:updated", "item:deleted"]:
        cache_clear()
        print("Cache cleared due to item event.")

    # Add more event handling as needed

    return jsonify({"status": "received"}), 200
