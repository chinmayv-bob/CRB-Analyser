import requests
from requests.auth import HTTPBasicAuth
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "https://businessonbot.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
# Fetch tickets from "Customer Reported Bugs and Feedback" created last month
JIRA_JQL = 'project = "Customer Reported Bugs and Feedback" AND created >= startOfMonth(-1) AND created <= endOfMonth(-1) ORDER BY created DESC'

def fetch_jira_tickets(limit=None):
    """
    Fetches tickets from Jira using JQL.
    If limit is None, fetches ALL tickets matching the JQL (handling pagination).
    If limit is specified, fetches up to that many tickets.
    """
    # Use standard JQL search endpoint
    
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    all_issues = []
    next_page_token = None
    batch_size = 100 # Max allowed by Jira is usually 100
    
    while True:
        # Check if we've reached the user-defined limit
        if limit and len(all_issues) >= limit:
            break
            
        current_max_results = batch_size
        if limit:
            remaining = limit - len(all_issues)
            if remaining < batch_size:
                current_max_results = remaining
    
        # Fetch tickets from November 1-30, 2025
        # Note: /rest/api/3/search/jql uses nextPageToken for pagination.
        query = {
            'jql': 'project = CRB AND created >= "2026-01-31" AND created <= "2026-02-01" ORDER BY created DESC',
            'maxResults': current_max_results,
            'fields': ['summary', 'description', 'status', 'comment', 'created', 'updated'] 
        }
        
        if next_page_token:
            query['nextPageToken'] = next_page_token
        
        try:
            logging.info(f"Fetching tickets (nextPageToken={'Present' if next_page_token else 'None'}, maxResults={current_max_results})...")
            
            # Switch to POST /search/jql as /search is deprecated
            search_url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
            response = requests.post(
                search_url,
                headers=headers,
                json=query,
                auth=auth
            )
            
            # Log response text if it fails
            if not response.ok:
                logging.error(f"Request failed: {response.status_code} - {response.text}")

            response.raise_for_status()
            
            data = response.json()
            issues = data.get('issues', [])
            # data.get('total') is not always present in search/jql responses
            next_page_token = data.get('nextPageToken')
            
            if not issues:
                break
                
            all_issues.extend(issues)
            logging.info(f"Fetched {len(issues)} tickets. Total so far: {len(all_issues)}")
            
            if not next_page_token:
                break
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching Jira tickets: {e}")
            if hasattr(e, 'response') and e.response is not None:
                 logging.error(f"Response content: {e.response.text}")
            break
            
    return all_issues

if __name__ == "__main__":
    # Test run
    tickets = fetch_jira_tickets(limit=5)
    if tickets:
        for ticket in tickets:
            print(f"[{ticket['key']}] {ticket['fields']['summary']}")
