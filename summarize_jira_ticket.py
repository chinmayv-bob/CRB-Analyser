import requests
import json
import logging
import time
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
SIM_AI_API_KEY = os.getenv("SIM_AI_API_KEY")
SIM_AI_WORKFLOW_ID = os.getenv("SIM_AI_WORKFLOW_ID")

def extract_text_from_adf(content):
    """
    Extracts plain text from Atlassian Document Format (ADF) JSON or HTML.
    This recursively traverses ADF structures and extracts only text content.
    """
    if not content:
        return ""
    
    # If it's a string, try to parse as JSON first
    if isinstance(content, str):
        # Try to parse as JSON (ADF format)
        try:
            content = json.loads(content)
        except (json.JSONDecodeError, ValueError):
            # Not JSON, just strip HTML tags
            clean = re.compile('<.*?>')
            return re.sub(clean, '', content)
    
    # Handle ADF JSON structures
    if isinstance(content, dict):
        text_parts = []
        
        # Extract text from "text" field
        if 'text' in content:
            text_parts.append(content['text'])
        
        # Recursively process "content" array
        if 'content' in content and isinstance(content['content'], list):
            for item in content['content']:
                text_parts.append(extract_text_from_adf(item))
        
        return ' '.join(filter(None, text_parts))
    
    # Handle lists (arrays of ADF nodes)
    if isinstance(content, list):
        text_parts = []
        for item in content:
            text_parts.append(extract_text_from_adf(item))
        return ' '.join(filter(None, text_parts))
    
    # Fallback: convert to string and strip HTML
    text = str(content)
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text) 

def summarize_ticket(ticket_data):
    """
    Sends ticket data to Sim.AI for summarization.
    """
    
    # Extract relevant fields
    key = ticket_data.get('key', '')
    fields = ticket_data.get('fields', {})
    summary = fields.get('summary', '')
    description = fields.get('description', '')
    status = fields.get('status', {}).get('name', '') if isinstance(fields.get('status'), dict) else str(fields.get('status', ''))
    priority = fields.get('priority', {}).get('name', '') if isinstance(fields.get('priority'), dict) else str(fields.get('priority', ''))
    
    # Jira description can be complex (Atlassian Document Format). 
    # For now, we'll just convert it to string if it's a dict/list, or use as is if string.
    if isinstance(description, (dict, list)):
        description_text = json.dumps(description)
    else:
        description_text = str(description)
    
    description_text = extract_text_from_adf(description_text)

    # Extract comments
    comments = []
    comment_data = fields.get('comment', {}).get('comments', [])
    for c in comment_data:
        author = c.get('author', {}).get('displayName', 'Unknown')
        created = c.get('created', '')
        body = c.get('body', '')
        if isinstance(body, (dict, list)):
            body_text = json.dumps(body)
        else:
            body_text = str(body)
        
        body_text = extract_text_from_adf(body_text)
        comments.append(f"{created};{author};{body_text}")
    
    comments_text = "\n".join(comments)
    
    # Calculate days (simplified - you may want to calculate actual values)
    created_date = fields.get('created', '')
    updated_date = fields.get('updated', '')
    days_in_status = 0  # Placeholder
    total_days_open = 0  # Placeholder
    
    url = f"https://www.sim.ai/api/workflows/{SIM_AI_WORKFLOW_ID}/execute"
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": SIM_AI_API_KEY,
    }
    
    # Match the exact structure expected by CRB.json workflow
    payload = {
        "ticket_id": key,
        "summary": summary,
        "description": description_text,
        "status": status,
        "priority": priority,
        "comments": comments_text,
        "days_in_status": days_in_status,
        "total_days_open": total_days_open
    }
    
    try:
        logging.info(f"Summarizing ticket {key}...")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 429:
             logging.warning("Rate limit hit. Waiting...")
             time.sleep(5)
             return summarize_ticket(ticket_data) # Retry

        response.raise_for_status()
        
        result = response.json()
        
        # Log the full response for debugging
        logging.info(f"Full API response: {json.dumps(result, indent=2)}")
        
        # Check if internal_comment is at the root level
        if "internal_comment" in result:
            return result["internal_comment"]
        
        # Extract the output - the workflow returns internal_comment in the final response
        output = result.get("output", {})
        
        # The InternalCommentWriter agent returns a JSON with "internal_comment"
        if isinstance(output, dict):
            internal_comment = output.get("internal_comment", "")
            if internal_comment:
                return internal_comment
            # Fallback to content if internal_comment not found
            content = output.get("content", "")
            if content:
                # Try to parse content as JSON if it's a string
                if isinstance(content, str):
                    try:
                        content_json = json.loads(content)
                        return content_json.get("internal_comment", content)
                    except:
                        return content
                return content
            return json.dumps(output)
        
        return str(output)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error summarizing ticket {key}: {e}")
        if hasattr(e, 'response') and e.response is not None:
             logging.error(f"Response content: {e.response.text}")
        return None
