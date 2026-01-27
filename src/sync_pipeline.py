"""
Sync Pipeline
Main orchestration for Kajabi → Excel → HubSpot sync
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Optional
import pandas as pd
from dotenv import load_dotenv

from .kajabi_client import KajabiClient
from .hubspot_client import HubSpotClient
from .excel_sync import ExcelSync

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/sync.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class SyncPipeline:
    """Main pipeline for syncing Kajabi orders to Excel and HubSpot"""

    # Email validation regex pattern
    EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def __init__(self):
        self.kajabi = KajabiClient()
        self.hubspot = HubSpotClient()
        self.excel = ExcelSync()
        self.last_sync_file = "data/last_sync.json"
        self.invalid_email_log = "logs/invalid_emails.log"

    def validate_email(self, email: str) -> bool:
        """
        Validate email format.
        Returns True if valid, False otherwise.
        """
        if not email or not isinstance(email, str):
            return False
        return bool(self.EMAIL_PATTERN.match(email.strip()))

    def log_invalid_email(self, email: str, name: str = "", reason: str = ""):
        """Log invalid email to separate file for review"""
        os.makedirs(os.path.dirname(self.invalid_email_log), exist_ok=True)
        timestamp = datetime.now().isoformat()
        with open(self.invalid_email_log, "a") as f:
            f.write(f"{timestamp} | Email: {email} | Name: {name} | Reason: {reason}\n")

    def get_last_sync_time(self) -> Optional[datetime]:
        """Get the timestamp of the last successful sync"""
        try:
            with open(self.last_sync_file, "r") as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get("last_sync"))
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return None

    def save_last_sync_time(self):
        """Save the current timestamp as last sync time"""
        os.makedirs(os.path.dirname(self.last_sync_file), exist_ok=True)
        with open(self.last_sync_file, "w") as f:
            json.dump({"last_sync": datetime.now().isoformat()}, f)

    def setup_hubspot_properties(self) -> bool:
        """Create custom properties in HubSpot if they don't exist"""
        logger.info("Setting up HubSpot custom properties...")
        try:
            results = self.hubspot.create_custom_properties()
            logger.info(f"HubSpot properties: {results}")
            return True
        except Exception as e:
            logger.error(f"Failed to create HubSpot properties: {e}")
            return False

    def sync_kajabi_orders(self, since: Optional[datetime] = None) -> dict:
        """
        Fetch new Kajabi orders and sync to Excel

        Args:
            since: Only fetch orders after this date (uses last sync if None)

        Returns:
            Dict with sync results
        """
        results = {"fetched": 0, "created": 0, "updated": 0, "errors": []}

        # Use last sync time if not specified
        if since is None:
            since = self.get_last_sync_time()

        logger.info(f"Fetching Kajabi orders since: {since or 'beginning'}")

        try:
            # Authenticate and fetch orders
            self.kajabi.authenticate()
            orders = self.kajabi.get_orders(since=since)
            results["fetched"] = len(orders)
            logger.info(f"Fetched {len(orders)} orders from Kajabi")

            # Load Excel spreadsheet
            self.excel.load_spreadsheet()

            # Process each order
            for order in orders:
                try:
                    result = self.excel.process_kajabi_order(order)
                    if result["status"] == "created":
                        results["created"] += 1
                    elif result["status"] == "updated":
                        results["updated"] += 1
                except Exception as e:
                    results["errors"].append(
                        {"order": order.get("id"), "error": str(e)}
                    )
                    logger.error(f"Error processing order: {e}")

            # Save Excel spreadsheet
            self.excel.save_spreadsheet()

            logger.info(
                f"Sync complete: {results['created']} created, "
                f"{results['updated']} updated, {len(results['errors'])} errors"
            )

        except Exception as e:
            logger.error(f"Kajabi sync failed: {e}")
            results["errors"].append({"type": "kajabi_fetch", "error": str(e)})

        return results

    def sync_to_hubspot(self) -> dict:
        """
        Sync all Excel subscribers to HubSpot

        Returns:
            Dict with sync results
        """
        results = {"processed": 0, "created": 0, "updated": 0, "skipped": 0, "errors": []}

        logger.info("Syncing subscribers to HubSpot...")

        try:
            subscribers = self.excel.get_all_subscribers()
            results["processed"] = len(subscribers)

            for subscriber in subscribers:
                try:
                    # Map Excel columns to HubSpot fields (use HubSpot property names)
                    contact_data = {
                        "email": subscriber.get("Email"),
                        "firstname": subscriber.get("Name"),
                        "lastname": subscriber.get("Last Name"),
                        "phone": subscriber.get("Phone"),
                        "address": subscriber.get("Street Address"),
                        "city": subscriber.get("City"),
                        "state": subscriber.get("St"),
                        "zip": str(subscriber.get("Zip", "")),
                        "credentials": subscriber.get("Credentials"),
                        "organization": subscriber.get("Organization"),
                        "specialty": subscriber.get("Specialty"),
                        "year_acquired": subscriber.get("Year Acquired"),
                        "courses_ordered": subscriber.get("Courses Ordered"),
                        "subscriber_number": subscriber.get("#Subscribers"),
                    }

                    # Skip if no email or NaN
                    if not contact_data["email"] or (isinstance(contact_data["email"], float) and pd.isna(contact_data["email"])):
                        results["skipped"] += 1
                        continue

                    # Strip whitespace from email
                    contact_data["email"] = str(contact_data["email"]).strip()

                    # Validate email format
                    if not self.validate_email(contact_data["email"]):
                        name = f"{subscriber.get('Name', '')} {subscriber.get('Last Name', '')}".strip()
                        self.log_invalid_email(
                            contact_data["email"],
                            name=name,
                            reason="Invalid email format"
                        )
                        logger.warning(f"Skipping invalid email: {contact_data['email']}")
                        results["skipped"] += 1
                        continue

                    # Check if exists and create/update
                    existing = self.hubspot.search_contact_by_email(
                        contact_data["email"]
                    )

                    if existing:
                        self.hubspot.update_contact(existing["id"], contact_data)
                        results["updated"] += 1
                    else:
                        self.hubspot.create_contact(contact_data)
                        results["created"] += 1

                except Exception as e:
                    results["errors"].append(
                        {"email": subscriber.get("Email"), "error": str(e)}
                    )
                    logger.error(f"Error syncing {subscriber.get('Email')}: {e}")

            logger.info(
                f"HubSpot sync complete: {results['created']} created, "
                f"{results['updated']} updated, {results['skipped']} skipped, "
                f"{len(results['errors'])} errors"
            )

        except Exception as e:
            logger.error(f"HubSpot sync failed: {e}")
            results["errors"].append({"type": "hubspot_sync", "error": str(e)})

        return results

    def run_full_sync(self) -> dict:
        """
        Run the complete sync pipeline:
        1. Fetch new Kajabi orders
        2. Update Excel spreadsheet
        3. Sync to HubSpot
        4. Save last sync timestamp

        Returns:
            Dict with full results
        """
        logger.info("=" * 50)
        logger.info("Starting full sync pipeline")
        logger.info("=" * 50)

        results = {
            "timestamp": datetime.now().isoformat(),
            "kajabi_sync": None,
            "hubspot_sync": None,
            "success": False,
        }

        try:
            # Step 1: Setup HubSpot properties (first run only)
            self.setup_hubspot_properties()

            # Step 2: Sync Kajabi orders to Excel
            results["kajabi_sync"] = self.sync_kajabi_orders()

            # Step 3: Sync Excel to HubSpot
            results["hubspot_sync"] = self.sync_to_hubspot()

            # Step 4: Save last sync time
            self.save_last_sync_time()

            results["success"] = True
            logger.info("Full sync completed successfully!")

        except Exception as e:
            logger.error(f"Full sync failed: {e}")
            results["error"] = str(e)

        logger.info("=" * 50)
        return results


# Entry point for running sync
if __name__ == "__main__":
    pipeline = SyncPipeline()
    results = pipeline.run_full_sync()

    print("\n" + "=" * 50)
    print("SYNC RESULTS")
    print("=" * 50)
    print(json.dumps(results, indent=2))
