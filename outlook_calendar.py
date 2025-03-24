import os
import requests
import msal
from dotenv import load_dotenv

load_dotenv()

# Microsoft Graph API credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

if not CLIENT_ID or not CLIENT_SECRET or not TENANT_ID:
    raise ValueError("Missing CLIENT_ID, CLIENT_SECRET, or TENANT_ID in environment variables.")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

def get_access_token():
    """Function to authenticates with Microsoft Graph API using Client Credentials Flow."""
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPES)
    
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Error authenticating with Microsoft Graph API: {result.get('error_description')}")

def get_calendar_events():
    """Function that etches Outlook Calendar events using Microsoft Graph API."""
    access_token = get_access_token()
    USER_ID = "dylan.gray@revenuepathgroup.com"

    url = f"https://graph.microsoft.com/v1.0/users/{USER_ID}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        events = response.json().get("value", [])
        return events
    else:
        print(f"Error fetching calendar events: {response.json()}")
        return []

def format_calendar_events():
    """Function that ormats calendar events into a readable schedule summary."""
    events = get_calendar_events()
    
    if not events:
        return "You have no events scheduled today."

    formatted_events = []
    for event in events:
        subject = event.get("subject", "No Title")
        start_time = event.get("start", {}).get("dateTime", "Unknown Time")
        end_time = event.get("end", {}).get("dateTime", "Unknown Time")
        
        formatted_events.append(f"- {subject}: {start_time} to {end_time}")
    
    return "Here is your schedule for today:\n" + "\n".join(formatted_events)
