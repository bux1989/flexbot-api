from flask import Flask
from tasks import tasks_bp
from projects import projects_bp
from sections import sections_bp
from labels import labels_bp
from ai import ai_bp
from filters import filters_bp
from collab import collab_bp

app = Flask(__name__)

# Register Blueprints for each module
app.register_blueprint(tasks_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(sections_bp)
app.register_blueprint(labels_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(filters_bp)
app.register_blueprint(collab_bp)

@app.route("/", methods=["GET"])
def index():
    return {"status": "FlexBot Todoist API running."}

if __name__ == "__main__":
    app.run(debug=True)
