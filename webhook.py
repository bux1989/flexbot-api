from flask import Blueprint, request, jsonify

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/todoist-webhook', methods=['POST'])
def todoist_webhook():
    # You can do whatever you want with the payload (log it, push to a queue, etc.)
    event = request.get_json()
    print("Received webhook event:", event)
    # Respond with 200 OK to acknowledge receipt
    return jsonify({"status": "received"}), 200
