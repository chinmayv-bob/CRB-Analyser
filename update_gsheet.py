import csv
import gspread
import logging
from google.oauth2.service_account import Credentials

# ---------------- LOGGING SETUP ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------- CONFIGURATION ----------------
SERVICE_ACCOUNT_FILE = os.getenv("GSHEETS_SERVICE_ACCOUNT_FILE", 'ticket-automation-478816-065d3bcabe7e.json')
SPREADSHEET_ID = os.getenv("GSHEETS_SPREADSHEET_ID")
SHEET_NAME = 'Analysis'
CSV_FILE = 'internal_comments-Jan.csv'

ISSUE_KEY_COLUMN_NAME = 'Issue key'
INTERNAL_COMMENTS_COLUMN_NAME = 'Internal comments.'


def map_comments():
    logger.info("Starting comment mapping process")

    # -------- Authenticate --------
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=scopes
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        logger.info("Authenticated and opened Google Sheet successfully")
    except Exception as e:
        logger.exception("Failed to authenticate or open Google Sheet")
        return

    # -------- Read CSV --------
    comments_map = {}
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row_num, row in enumerate(reader, start=1):
                if len(row) < 2:
                    logger.warning(f"Skipping CSV row {row_num}: insufficient columns")
                    continue

                issue_key = row[0].strip().upper()
                comment = row[1].strip()
                comments_map[issue_key] = comment

        logger.info(f"Loaded {len(comments_map)} comments from CSV")

    except FileNotFoundError:
        logger.error(f"CSV file not found: {CSV_FILE}")
        return
    except Exception as e:
        logger.exception("Error while reading CSV file")
        return

    # -------- Read Sheet --------
    try:
        all_values = sheet.get_all_values()
        if not all_values:
            logger.error("Google Sheet is empty")
            return

        headers = all_values[0]
        logger.info(f"Sheet headers detected: {headers}")

        issue_key_idx = headers.index(ISSUE_KEY_COLUMN_NAME)
        comments_idx = headers.index(INTERNAL_COMMENTS_COLUMN_NAME)

    except ValueError as e:
        logger.error(
            f"Required column missing. "
            f"Expected '{ISSUE_KEY_COLUMN_NAME}' and '{INTERNAL_COMMENTS_COLUMN_NAME}'"
        )
        return
    except Exception as e:
        logger.exception("Failed while reading sheet headers")
        return

    # -------- Prepare Updates --------
    updates = []
    matched_keys = set()

    for i, row in enumerate(all_values[1:], start=2):
        if issue_key_idx >= len(row):
            logger.warning(f"Row {i} missing Issue key column, skipping")
            continue

        sheet_issue_key = row[issue_key_idx].strip().upper()

        if sheet_issue_key in comments_map:
            updates.append({
                'range': gspread.utils.rowcol_to_a1(i, comments_idx + 1),
                'values': [[comments_map[sheet_issue_key]]]
            })
            matched_keys.add(sheet_issue_key)

    logger.info(f"Matched {len(matched_keys)} issue keys")

    # -------- Execute Update --------
    if not updates:
        logger.warning("No matching issue keys found. Nothing to update.")
        return

    try:
        logger.info(f"Updating {len(updates)} rows in Google Sheet")
        sheet.batch_update(updates)
        logger.info("Comments updated successfully")
    except Exception as e:
        logger.exception("Failed during batch update")


if __name__ == "__main__":
    map_comments()
