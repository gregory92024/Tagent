"""
Email Tracking Module
Tracks email reminder status for renewal workflow
"""

import json
import os
from datetime import datetime
from typing import Optional


class EmailTracker:
    """Tracks email reminder status and conversions for renewal workflow"""

    def __init__(self, tracking_file: str = "data/email_tracking.json"):
        self.tracking_file = tracking_file
        self.data = self._load()

    def _load(self) -> dict:
        """Load tracking data from JSON file"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Return default structure if file doesn't exist or is invalid
        return {
            "contacts": {},
            "last_check": None
        }

    def _save(self) -> None:
        """Save tracking data to JSON file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.tracking_file), exist_ok=True)

        with open(self.tracking_file, "w") as f:
            json.dump(self.data, f, indent=2, default=str)

    def get_contact_status(self, subscriber_id: str) -> Optional[dict]:
        """
        Get tracking status for a specific contact.

        Args:
            subscriber_id: The subscriber ID to look up

        Returns:
            Dict with contact tracking info or None if not tracked
        """
        return self.data["contacts"].get(str(subscriber_id))

    def add_contact(self, subscriber_id: str, email: str, payment_date: str) -> dict:
        """
        Add a new contact to tracking.

        Args:
            subscriber_id: Unique subscriber identifier
            email: Contact email address
            payment_date: ISO format date of last payment

        Returns:
            The created contact record
        """
        subscriber_id = str(subscriber_id)

        if subscriber_id in self.data["contacts"]:
            return self.data["contacts"][subscriber_id]

        contact = {
            "email": email,
            "payment_date": payment_date,
            "reminder_1_sent": None,
            "reminder_2_sent": None,
            "reminder_3_sent": None,
            "status": "pending",
            "response_date": None,
            "conversion_date": None
        }

        self.data["contacts"][subscriber_id] = contact
        self._save()
        return contact

    def record_email_sent(self, subscriber_id: str, reminder_num: int) -> bool:
        """
        Record that a reminder email was sent.

        Args:
            subscriber_id: The subscriber ID
            reminder_num: Which reminder (1, 2, or 3)

        Returns:
            True if successful, False if contact not found
        """
        subscriber_id = str(subscriber_id)

        if subscriber_id not in self.data["contacts"]:
            return False

        if reminder_num not in (1, 2, 3):
            return False

        field = f"reminder_{reminder_num}_sent"
        self.data["contacts"][subscriber_id][field] = datetime.now().strftime("%Y-%m-%d")
        self._save()
        return True

    def record_response(self, subscriber_id: str) -> bool:
        """
        Record that a contact responded to an email.

        Args:
            subscriber_id: The subscriber ID

        Returns:
            True if successful, False if contact not found
        """
        subscriber_id = str(subscriber_id)

        if subscriber_id not in self.data["contacts"]:
            return False

        self.data["contacts"][subscriber_id]["status"] = "responded"
        self.data["contacts"][subscriber_id]["response_date"] = datetime.now().strftime("%Y-%m-%d")
        self._save()
        return True

    def record_conversion(self, subscriber_id: str, payment_date: Optional[str] = None) -> bool:
        """
        Record that a contact converted (made a new purchase).

        Args:
            subscriber_id: The subscriber ID
            payment_date: Optional date of the new payment (ISO format)

        Returns:
            True if successful, False if contact not found
        """
        subscriber_id = str(subscriber_id)

        if subscriber_id not in self.data["contacts"]:
            return False

        self.data["contacts"][subscriber_id]["status"] = "converted"
        self.data["contacts"][subscriber_id]["conversion_date"] = (
            payment_date or datetime.now().strftime("%Y-%m-%d")
        )
        self._save()
        return True

    def mark_lapsed(self, subscriber_id: str) -> bool:
        """
        Mark a contact as lapsed (didn't renew after all reminders).

        Args:
            subscriber_id: The subscriber ID

        Returns:
            True if successful, False if contact not found
        """
        subscriber_id = str(subscriber_id)

        if subscriber_id not in self.data["contacts"]:
            return False

        self.data["contacts"][subscriber_id]["status"] = "lapsed"
        self._save()
        return True

    def get_next_reminder_num(self, subscriber_id: str) -> Optional[int]:
        """
        Determine which reminder number should be sent next.

        Args:
            subscriber_id: The subscriber ID

        Returns:
            1, 2, or 3 for next reminder, or None if all sent or not applicable
        """
        contact = self.get_contact_status(str(subscriber_id))

        if not contact:
            return 1  # New contact, start with reminder 1

        # Don't send more reminders if responded or converted
        if contact["status"] in ("responded", "converted", "lapsed"):
            return None

        # Determine next reminder based on what's been sent
        if not contact.get("reminder_1_sent"):
            return 1
        elif not contact.get("reminder_2_sent"):
            return 2
        elif not contact.get("reminder_3_sent"):
            return 3

        return None  # All reminders sent

    def get_pending_reminders(self) -> list:
        """
        Get contacts that have pending reminders (haven't responded/converted).

        Returns:
            List of dicts with subscriber_id and current status
        """
        pending = []

        for subscriber_id, contact in self.data["contacts"].items():
            if contact["status"] == "pending":
                next_reminder = self.get_next_reminder_num(subscriber_id)
                if next_reminder:
                    pending.append({
                        "subscriber_id": subscriber_id,
                        "email": contact["email"],
                        "payment_date": contact.get("payment_date"),
                        "next_reminder": next_reminder,
                        "reminder_1_sent": contact.get("reminder_1_sent"),
                        "reminder_2_sent": contact.get("reminder_2_sent"),
                        "reminder_3_sent": contact.get("reminder_3_sent"),
                    })

        return pending

    def get_all_tracked(self) -> dict:
        """Get all tracked contacts with their status"""
        return self.data["contacts"].copy()

    def get_stats(self) -> dict:
        """
        Get summary statistics of tracking data.

        Returns:
            Dict with counts by status
        """
        stats = {
            "total_tracked": 0,
            "pending": 0,
            "responded": 0,
            "converted": 0,
            "lapsed": 0,
            "reminder_1_sent": 0,
            "reminder_2_sent": 0,
            "reminder_3_sent": 0,
        }

        for contact in self.data["contacts"].values():
            stats["total_tracked"] += 1
            status = contact.get("status", "pending")
            if status in stats:
                stats[status] += 1

            if contact.get("reminder_1_sent"):
                stats["reminder_1_sent"] += 1
            if contact.get("reminder_2_sent"):
                stats["reminder_2_sent"] += 1
            if contact.get("reminder_3_sent"):
                stats["reminder_3_sent"] += 1

        return stats

    def update_last_check(self) -> None:
        """Update the timestamp of the last check"""
        self.data["last_check"] = datetime.now().isoformat()
        self._save()


# Quick test when run directly
if __name__ == "__main__":
    tracker = EmailTracker()
    print(f"Tracking data: {tracker.data}")
    print(f"Stats: {tracker.get_stats()}")
