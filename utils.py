import requests

def get_headers(api_key):
    """
    Returns headers for Todoist API requests, using the user-supplied API key.
    """
    if not api_key:
        raise ValueError("No Todoist API key provided.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def get_all_tasks(api_key):
    """
    Fetch all active Todoist tasks for the provided API key.
    """
    headers = get_headers(api_key)
    resp = requests.get("https://api.todoist.com/rest/v2/tasks", headers=headers)
    return resp.json()

def get_completed_tasks(api_key):
    """
    Fetch all completed Todoist tasks for the provided API key.
    """
    headers = get_headers(api_key)
    resp = requests.get("https://api.todoist.com/sync/v9/completed/get_all", headers=headers)
    return resp.json()
