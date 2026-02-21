import csv
import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from fetch_jira_tickets import fetch_jira_tickets
from summarize_jira_ticket import summarize_ticket

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OUTPUT_CSV = "internal_comments-Jan.csv"
MAX_RETRIES = 10
NUM_THREADS = 10

# Thread-safe CSV writing
csv_lock = Lock()

def process_ticket_with_retry(ticket):
    """
    Process a single ticket with retry logic.
    Returns: (ticket_id, internal_comment, success)
    """
    key = ticket.get('key')
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Processing {key} (attempt {attempt}/{MAX_RETRIES})...")
            
            # Call Sim.AI to get internal comment
            internal_comment = summarize_ticket(ticket)
            
            if internal_comment:
                logging.info(f"✓ Successfully processed {key}")
                return (key, internal_comment, True)
            else:
                logging.warning(f"Empty response for {key}, attempt {attempt}/{MAX_RETRIES}")
                
        except Exception as e:
            logging.error(f"Error processing {key} (attempt {attempt}/{MAX_RETRIES}): {e}")
            
        # Wait before retry (exponential backoff)
        if attempt < MAX_RETRIES:
            wait_time = 5 ** attempt  # 2, 4, 8 seconds
            logging.info(f"Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    
    logging.error(f"✗ Failed to process {key} after {MAX_RETRIES} attempts")
    return (key, None, False)

def write_to_csv(ticket_id, internal_comment):
    """Thread-safe CSV writing"""
    with csv_lock:
        file_exists = os.path.isfile(OUTPUT_CSV)
        with open(OUTPUT_CSV, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ticket_id', 'internal_comment']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'ticket_id': ticket_id,
                'internal_comment': internal_comment
            })

def main():
    logging.info("Starting Jira CRB Analysis...")
    
    # 1. Fetch Tickets (fetch all)
    tickets = fetch_jira_tickets(limit=None)
    
    if not tickets:
        logging.warning("No tickets found or failed to fetch.")
        return
    
    logging.info(f"Fetched {len(tickets)} tickets. Processing with {NUM_THREADS} threads...")
    
    # 2. Process tickets concurrently
    successful = 0
    failed = 0
    failed_tickets = []
    
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        # Submit all tickets for processing
        future_to_ticket = {executor.submit(process_ticket_with_retry, ticket): ticket for ticket in tickets}
        
        # Process results as they complete
        for future in as_completed(future_to_ticket):
            ticket_id, internal_comment, success = future.result()
            
            if success:
                write_to_csv(ticket_id, internal_comment)
                successful += 1
            else:
                failed += 1
                failed_tickets.append(ticket_id)
    
    # 3. Summary
    logging.info("=" * 60)
    logging.info(f"Analysis complete!")
    logging.info(f"Total tickets: {len(tickets)}")
    logging.info(f"✓ Successful: {successful}")
    logging.info(f"✗ Failed: {failed}")
    
    if failed_tickets:
        logging.error(f"Failed tickets: {', '.join(failed_tickets)}")
    else:
        logging.info("All tickets processed successfully!")
    logging.info("=" * 60)

if __name__ == "__main__":
    main()
