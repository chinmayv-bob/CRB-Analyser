import requests
from requests.auth import HTTPBasicAuth
import json
import logging

logging.basicConfig(level=logging.INFO)

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "https://businessonbot.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def inspect_fields():
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # specific query with date restriction to avoid unbounded error
    query = {
        'jql': 'created >= startOfMonth(-1) order by created DESC',
        'maxResults': 1,
        'fields': ['*all']
    }

    try:
        response = requests.post(url, headers=headers, json=query, auth=auth)
        response.raise_for_status()
        data = response.json()
        issues = data.get('issues', [])
        if issues:
            ticket = issues[0]
            fields = ticket.get('fields', {})
            print(f"Ticket Key: {ticket.get('key')}")
            print(f"Total Fields Available: {len(fields)}")
            print("-" * 30)
            
            # Print field names and their types/values (simplified)
            for field_name, value in fields.items():
                # specific check for interesting fields
                if value is not None:
                     if isinstance(value, dict):
                         print(f"{field_name}: (dict) keys: {list(value.keys())}")
                         # print subset for context if small
                     elif isinstance(value, list):
                         print(f"{field_name}: (list) length: {len(value)}")
                     else:
                         print(f"{field_name}: {type(value).__name__} = {str(value)[:50]}...")
            
            # Dump full keys to a file for review if needed
            with open("available_fields.json", "w") as f:
                json.dump(list(fields.keys()), f, indent=2)
                
        else:
            print("No tickets found.")
            
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(e.response.text)

if __name__ == "__main__":
    inspect_fields()
