import os
import requests

def get_headers():
    """
    Returns headers for Todoist API requests using the API key from environment.
    """
    api_key = os.getenv("TODOIST_API_KEY")
    if not api_key:
        raise ValueError("TODOIST_API_KEY environment variable not set.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def get_all_tasks():
    """
    Fetch all active Todoist tasks using the environment API key.
    """
    headers = get_headers()
    resp = requests.get("https://api.todoist.com/rest/v2/tasks", headers=headers)
    return resp.json()

def get_completed_tasks():
    """
    Fetch all completed Todoist tasks using the environment API key.
    """
    headers = get_headers()
    resp = requests.get("https://api.todoist.com/sync/v9/completed/get_all", headers=headers)
    return resp.json()
