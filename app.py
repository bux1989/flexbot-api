from flask import Flask, request, jsonify
from tasks import tasks_bp
from projects import projects_bp
from sections import sections_bp
from labels import labels_bp
from ai import ai_bp
from filters import filters_bp
from collab import collab_bp
from webhook import webhook_bp
from edit_tasks import edit_tasks_bp

import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Log blueprint registration
def log_and_register_blueprint(blueprint, url_prefix=None):
    if url_prefix:
        logger.info(f"Registering blueprint: {blueprint.name} at prefix: {url_prefix}")
        app.register_blueprint(blueprint, url_prefix=url_prefix)
    else:
        logger.info(f"Registering blueprint: {blueprint.name}")
        app.register_blueprint(blueprint)

log_and_register_blueprint(tasks_bp)
log_and_register_blueprint(projects_bp)
log_and_register_blueprint(sections_bp)
log_and_register_blueprint(labels_bp)
log_and_register_blueprint(ai_bp)
log_and_register_blueprint(filters_bp)
log_and_register_blueprint(collab_bp)
log_and_register_blueprint(webhook_bp)
log_and_register_blueprint(edit_tasks_bp, url_prefix="/tasks")

@app.route("/", methods=["GET"])
def index():
    logger.debug("Index route called")
    return {"status": "FlexBot Todoist API running."}

# Log all URL rules for enhanced debugging
def log_url_rules():
    logger.info("\n=== Registered URL Rules ===")
    for rule in app.url_map.iter_rules():
        logger.info(rule)
    logger.info("=== End of URL Rules ===\n")

# Always log URL rules at startup, even with Gunicorn
with app.app_context():
    log_url_rules()

# Optionally log every request (for extra debugging)
@app.before_request
def log_request_info():
    logger.debug(f"Handling {request.method} request for {request.url}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug(f"Request body: {request.get_data()}")

# Optionally log responses (for debugging responses)
@app.after_request
def log_response_info(response):
    logger.debug(f"Response status: {response.status}")
    logger.debug(f"Response data: {response.get_data(as_text=True)}")
    return response

# Enhanced error handler (shows errors in logs)
@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception(f"Exception occurred: {e}")
    response = jsonify({"error": str(e)})
    response.status_code = 500
    return response

if __name__ == "__main__":
    logger.info("Starting FlexBot Todoist API (debug mode)...")
    app.run(debug=True)
