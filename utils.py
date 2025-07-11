import os

# Get Todoist API key from environment variable
TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")
if not TODOIST_API_KEY:
    raise ValueError("TODOIST_API_KEY environment variable not set.")

HEADERS = {
    "Authorization": f"Bearer {TODOIST_API_KEY}",
    "Content-Type": "application/json"
}

# --- Add any helper functions here ---

def get_all_tasks():
    """Return all active Todoist tasks."""
    import requests
    resp = requests.get("https://api.todoist.com/rest/v2/tasks", headers=HEADERS)
    return resp.json()

def get_completed_tasks():
    """Return all completed Todoist tasks."""
    import requests
    resp = requests.get("https://api.todoist.com/sync/v9/completed/get_all", headers=HEADERS)
    return resp.json()
