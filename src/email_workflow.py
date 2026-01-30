"""
Email Workflow Module
Identifies renewal candidates and manages email workflow logic
"""

import os
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional, TYPE_CHECKING
import pandas as pd

from .excel_sync import ExcelSync
from .email_tracking import EmailTracker

if TYPE_CHECKING:
    from .kajabi_client import KajabiClient


class EmailWorkflow:
    """Handles renewal candidate identification and email workflow logic"""

    # Exclusion strings to check in Courses Ordered column
    EXCLUSION_STRINGS = [
        "COMPETITOR",
        "DON'T SEND MARKETING",
    ]

    # Renewal cycle configuration
    RENEWAL_CYCLE_MONTHS = 24  # 2 years
    REMINDER_MONTHS_BEFORE = 6  # Send reminder 6 months before renewal
    REMINDER_START_MONTHS = 18  # 24 - 6 = 18 months after payment

    # Escalating reminder schedule (months after payment)
    REMINDER_1_MONTHS = 18  # 6 months before renewal
    REMINDER_2_MONTHS = 21  # 3 months before renewal
    REMINDER_3_MONTHS = 23  # 1 month before renewal

    # Template file location
    TEMPLATE_FILE = "templates/renewal_reminder.txt"

    def __init__(self, excel_sync: Optional[ExcelSync] = None):
        self.excel = excel_sync or ExcelSync()

    def parse_payment_date(self, payment_value) -> Optional[datetime]:
        """
        Parse payment date from various formats.

        Handles:
        - datetime objects
        - Timestamp objects
        - Strings like "online 5.11.25" or "5.11.25"
        - Standard date strings

        Returns:
            datetime object or None if unparseable
        """
        if pd.isna(payment_value):
            return None

        # Already a datetime
        if isinstance(payment_value, datetime):
            return payment_value

        # Pandas Timestamp
        if isinstance(payment_value, pd.Timestamp):
            return payment_value.to_pydatetime()

        # String parsing
        if isinstance(payment_value, str):
            payment_str = payment_value.strip()

            # Remove common prefixes like "online"
            payment_str = re.sub(r'^(online|check|cash|cc)\s*', '', payment_str, flags=re.IGNORECASE)
            payment_str = payment_str.strip()

            if not payment_str:
                return None

            # Try various date formats
            date_formats = [
                "%m.%d.%y",      # 5.11.25
                "%m/%d/%y",      # 5/11/25
                "%m-%d-%y",      # 5-11-25
                "%m.%d.%Y",      # 5.11.2025
                "%m/%d/%Y",      # 5/11/2025
                "%m-%d-%Y",      # 5-11-2025
                "%Y-%m-%d",      # 2025-05-11
                "%Y/%m/%d",      # 2025/05/11
                "%d.%m.%y",      # 11.5.25 (European)
                "%d/%m/%y",      # 11/5/25 (European)
            ]

            for fmt in date_formats:
                try:
                    return datetime.strptime(payment_str, fmt)
                except ValueError:
                    continue

            # Try pandas date parser as fallback
            try:
                return pd.to_datetime(payment_str).to_pydatetime()
            except (ValueError, TypeError):
                return None

        return None

    def check_exclusions(self, row: dict) -> tuple[bool, str]:
        """
        Check if a contact should be excluded from emails.

        Args:
            row: Dict representing a subscriber row

        Returns:
            Tuple of (excluded: bool, reason: str)
        """
        # Check for valid email
        email = row.get("Email", "")
        if pd.isna(email) or not email or str(email).strip() == "":
            return True, "No email address"

        # Check Email 2 as backup
        email2 = row.get("Email 2", "")
        email_str = str(email).strip()
        if not email_str or email_str.lower() == "nan":
            if pd.isna(email2) or not email2 or str(email2).strip() == "":
                return True, "No email address"

        # Check exclusion strings in Courses Ordered
        courses = row.get("Courses Ordered", "")
        if not pd.isna(courses) and courses:
            courses_upper = str(courses).upper()
            for exclusion in self.EXCLUSION_STRINGS:
                if exclusion in courses_upper:
                    return True, f"Excluded: {exclusion}"

        return False, ""

    def get_renewal_candidates(self) -> list[dict]:
        """
        Find contacts who are 18-24 months since payment (renewal reminder window).

        Returns:
            List of candidate dicts with subscriber info
        """
        if self.excel.df is None:
            self.excel.load_spreadsheet()

        candidates = []
        today = datetime.now()

        # Calculate date boundaries
        # Renewal window: 18-24 months since payment
        reminder_start = today - relativedelta(months=self.RENEWAL_CYCLE_MONTHS)  # 24 months ago
        reminder_end = today - relativedelta(months=self.REMINDER_START_MONTHS)   # 18 months ago

        for idx, row in self.excel.df.iterrows():
            row_dict = row.to_dict()

            # Parse payment date
            payment_date = self.parse_payment_date(row.get("Payment"))
            if payment_date is None:
                continue

            # Check if in renewal window (18-24 months since payment)
            if reminder_start <= payment_date <= reminder_end:
                # Check exclusions
                excluded, reason = self.check_exclusions(row_dict)
                if excluded:
                    continue

                # Calculate months since payment
                months_since = relativedelta(today, payment_date).years * 12 + relativedelta(today, payment_date).months

                # Handle both column name variants
                subscriber_id = row.get("#", row.get("#Subscribers", idx))
                name = row.get("Subscribers Name", row.get("Name", ""))

                candidates.append({
                    "subscriber_id": subscriber_id,
                    "name": name,
                    "last_name": row.get("Last Name", ""),
                    "email": row.get("Email", ""),
                    "payment_date": payment_date,
                    "months_since_payment": months_since,
                    "courses_ordered": row.get("Courses Ordered", ""),
                })

        return candidates

    def get_status_counts(self) -> dict:
        """
        Get counts of subscribers by renewal status.

        Returns:
            Dict with status counts
        """
        if self.excel.df is None:
            self.excel.load_spreadsheet()

        today = datetime.now()

        # Calculate boundaries
        renewal_boundary = today - relativedelta(months=self.RENEWAL_CYCLE_MONTHS)  # 24 months ago
        reminder_boundary = today - relativedelta(months=self.REMINDER_START_MONTHS)  # 18 months ago

        counts = {
            "total": len(self.excel.df),
            "renewal_candidates": 0,
            "lapsed": 0,
            "current": 0,
            "no_payment_date": 0,
            "excluded_no_email": 0,
            "excluded_competitor": 0,
            "excluded_marketing_optout": 0,
        }

        for idx, row in self.excel.df.iterrows():
            row_dict = row.to_dict()
            payment_date = self.parse_payment_date(row.get("Payment"))

            if payment_date is None:
                counts["no_payment_date"] += 1
                continue

            # Check exclusions first
            excluded, reason = self.check_exclusions(row_dict)
            if excluded:
                if "No email" in reason:
                    counts["excluded_no_email"] += 1
                elif "COMPETITOR" in reason:
                    counts["excluded_competitor"] += 1
                elif "MARKETING" in reason:
                    counts["excluded_marketing_optout"] += 1
                continue

            # Categorize by payment date
            if payment_date < renewal_boundary:
                counts["lapsed"] += 1
            elif renewal_boundary <= payment_date <= reminder_boundary:
                counts["renewal_candidates"] += 1
            else:
                counts["current"] += 1

        return counts

    def generate_renewal_report(self, verbose: bool = True) -> dict:
        """
        Generate a comprehensive renewal report.

        Args:
            verbose: If True, print detailed output

        Returns:
            Dict with report data
        """
        counts = self.get_status_counts()
        candidates = self.get_renewal_candidates()

        today = datetime.now()
        renewal_boundary = today - relativedelta(months=self.RENEWAL_CYCLE_MONTHS)
        reminder_boundary = today - relativedelta(months=self.REMINDER_START_MONTHS)

        report = {
            "generated_at": today.isoformat(),
            "date_range": {
                "reminder_window_start": reminder_boundary.strftime("%Y-%m-%d"),
                "reminder_window_end": renewal_boundary.strftime("%Y-%m-%d"),
            },
            "counts": counts,
            "candidates": candidates,
        }

        if verbose:
            print("\n" + "=" * 60)
            print("RENEWAL REMINDER REPORT")
            print("=" * 60)
            print(f"Generated: {today.strftime('%Y-%m-%d %H:%M')}")
            print(f"\nRenewal Window: Payment between {renewal_boundary.strftime('%Y-%m-%d')} and {reminder_boundary.strftime('%Y-%m-%d')}")
            print(f"(18-24 months since payment)")

            print("\n" + "-" * 40)
            print("STATUS SUMMARY")
            print("-" * 40)
            print(f"Total records:           {counts['total']:>6}")
            print(f"Renewal candidates:      {counts['renewal_candidates']:>6}")
            print(f"Lapsed (>24 months):     {counts['lapsed']:>6}")
            print(f"Current (<18 months):    {counts['current']:>6}")
            print(f"No payment date:         {counts['no_payment_date']:>6}")

            print("\n" + "-" * 40)
            print("EXCLUSIONS")
            print("-" * 40)
            print(f"No email address:        {counts['excluded_no_email']:>6}")
            print(f"Competitor:              {counts['excluded_competitor']:>6}")
            print(f"Marketing opt-out:       {counts['excluded_marketing_optout']:>6}")

        return report

    def print_candidate_list(self):
        """Print formatted list of renewal candidates."""
        candidates = self.get_renewal_candidates()

        print("\n" + "=" * 80)
        print("RENEWAL CANDIDATES")
        print("=" * 80)
        print(f"{'#':<6} {'Name':<25} {'Email':<35} {'Payment Date':<12} {'Months'}")
        print("-" * 80)

        for c in candidates:
            name = f"{c['name']} {c['last_name']}".strip()[:24]
            email = str(c['email'])[:34]
            payment = c['payment_date'].strftime('%Y-%m-%d')
            months = c['months_since_payment']
            sub_id = c.get('subscriber_id', 'N/A')

            print(f"{sub_id:<6} {name:<25} {email:<35} {payment:<12} {months}")

        print("-" * 80)
        print(f"Total candidates: {len(candidates)}")

    def check_conversions(self, kajabi_client: "KajabiClient", tracker: EmailTracker) -> list:
        """
        Check if any tracked contacts made new purchases in Kajabi.

        Args:
            kajabi_client: Authenticated Kajabi client
            tracker: EmailTracker instance

        Returns:
            List of conversions detected (subscriber_id, payment_date)
        """
        conversions = []
        tracked = tracker.get_all_tracked()

        if not tracked:
            return conversions

        # Get recent Kajabi purchases (last 30 days as a reasonable window)
        try:
            since = datetime.now() - relativedelta(days=30)
            recent_purchases = kajabi_client.get_orders(since=since, limit=200)
        except Exception as e:
            print(f"Warning: Could not fetch Kajabi purchases: {e}")
            return conversions

        # Build lookup of tracked emails
        email_to_subscriber = {}
        for subscriber_id, contact in tracked.items():
            if contact.get("status") == "pending":
                email = contact.get("email", "").lower()
                if email:
                    email_to_subscriber[email] = subscriber_id

        # Check each recent purchase against tracked contacts
        for purchase in recent_purchases:
            # Get customer email from purchase
            # Note: May need to fetch customer details separately
            customer_email = purchase.get("email", "").lower()

            if customer_email in email_to_subscriber:
                subscriber_id = email_to_subscriber[customer_email]
                payment_date = purchase.get("created_at", "")[:10]  # Extract date portion

                # Record conversion
                tracker.record_conversion(subscriber_id, payment_date)
                conversions.append({
                    "subscriber_id": subscriber_id,
                    "email": customer_email,
                    "payment_date": payment_date,
                })

        return conversions

    def get_reminder_threshold(self, reminder_num: int) -> int:
        """Get months since payment threshold for a reminder number."""
        thresholds = {
            1: self.REMINDER_1_MONTHS,  # 18 months
            2: self.REMINDER_2_MONTHS,  # 21 months
            3: self.REMINDER_3_MONTHS,  # 23 months
        }
        return thresholds.get(reminder_num, 18)

    def get_due_reminders(self, tracker: EmailTracker) -> list:
        """
        Get contacts due for their next reminder based on payment date and tracking.

        Logic:
        - Reminder 1: 18+ months since payment, reminder 1 not sent
        - Reminder 2: 21+ months since payment, reminder 1 sent, reminder 2 not sent
        - Reminder 3: 23+ months since payment, reminder 2 sent, reminder 3 not sent

        Args:
            tracker: EmailTracker instance

        Returns:
            List of dicts with contact info and which reminder is due
        """
        due_reminders = []
        today = datetime.now()

        # Get all renewal candidates from spreadsheet
        candidates = self.get_renewal_candidates()

        for candidate in candidates:
            subscriber_id = str(candidate.get("subscriber_id"))
            payment_date = candidate.get("payment_date")
            months_since = candidate.get("months_since_payment", 0)

            # Get or create tracking record
            contact_status = tracker.get_contact_status(subscriber_id)

            if contact_status:
                # Skip if already responded or converted
                if contact_status.get("status") in ("responded", "converted", "lapsed"):
                    continue

                # Determine next reminder
                next_reminder = tracker.get_next_reminder_num(subscriber_id)
            else:
                # New contact, add to tracking
                tracker.add_contact(
                    subscriber_id=subscriber_id,
                    email=candidate.get("email", ""),
                    payment_date=payment_date.strftime("%Y-%m-%d") if payment_date else None
                )
                next_reminder = 1
                contact_status = tracker.get_contact_status(subscriber_id)

            if not next_reminder:
                continue

            # Check if enough time has passed for this reminder
            threshold_months = self.get_reminder_threshold(next_reminder)

            if months_since >= threshold_months:
                due_reminders.append({
                    "subscriber_id": subscriber_id,
                    "name": candidate.get("name", ""),
                    "last_name": candidate.get("last_name", ""),
                    "email": candidate.get("email", ""),
                    "payment_date": payment_date,
                    "months_since_payment": months_since,
                    "courses_ordered": candidate.get("courses_ordered", ""),
                    "reminder_num": next_reminder,
                    "reminder_1_sent": contact_status.get("reminder_1_sent") if contact_status else None,
                    "reminder_2_sent": contact_status.get("reminder_2_sent") if contact_status else None,
                })

        return due_reminders

    def load_email_template(self) -> str:
        """
        Load the email template from file.

        Returns:
            Template string or default if file not found
        """
        if os.path.exists(self.TEMPLATE_FILE):
            with open(self.TEMPLATE_FILE, "r") as f:
                return f.read()

        # Default template
        return """Subject: Your TeachCE Certification Renewal

Dear {first_name},

Your continuing education credits are due for renewal. Your last order was on {payment_date} for {courses_ordered}.

To maintain your certification, you'll need to complete your renewal by {renewal_deadline}.

Questions? Contact us for assistance.

Best regards,
TeachCE Team
"""

    def generate_email(self, contact: dict) -> str:
        """
        Generate a personalized email from template.

        Args:
            contact: Dict with contact details (from get_due_reminders)

        Returns:
            Filled email template string
        """
        template = self.load_email_template()

        # Calculate renewal deadline (24 months from payment)
        payment_date = contact.get("payment_date")
        if isinstance(payment_date, datetime):
            renewal_deadline = payment_date + relativedelta(months=self.RENEWAL_CYCLE_MONTHS)
            payment_str = payment_date.strftime("%B %d, %Y")
            deadline_str = renewal_deadline.strftime("%B %d, %Y")
        else:
            payment_str = str(payment_date) if payment_date else "N/A"
            deadline_str = "N/A"

        # Fill in template
        email = template.format(
            first_name=contact.get("name", "Valued Customer"),
            last_name=contact.get("last_name", ""),
            email=contact.get("email", ""),
            subscriber_id=contact.get("subscriber_id", ""),
            payment_date=payment_str,
            courses_ordered=contact.get("courses_ordered", "N/A") or "N/A",
            renewal_deadline=deadline_str,
        )

        return email

    def run_daily_check(self, kajabi_client: Optional["KajabiClient"] = None) -> dict:
        """
        Run the daily renewal check.

        Steps:
        1. Load tracking data
        2. Check for conversions (if Kajabi client provided)
        3. Identify contacts due for reminders
        4. Generate report
        5. Save updated tracking state

        Args:
            kajabi_client: Optional Kajabi client for conversion checking

        Returns:
            Dict with check results
        """
        tracker = EmailTracker()

        results = {
            "timestamp": datetime.now().isoformat(),
            "conversions": [],
            "due_reminders": [],
            "stats": {},
        }

        # Check for conversions if Kajabi client available
        if kajabi_client:
            try:
                conversions = self.check_conversions(kajabi_client, tracker)
                results["conversions"] = conversions
            except Exception as e:
                print(f"Warning: Conversion check failed: {e}")

        # Get contacts due for reminders
        due_reminders = self.get_due_reminders(tracker)
        results["due_reminders"] = due_reminders

        # Update stats
        results["stats"] = tracker.get_stats()

        # Update last check timestamp
        tracker.update_last_check()

        return results

    def print_daily_check_report(self, results: dict) -> None:
        """Print formatted daily check report."""
        print("\n" + "=" * 60)
        print("DAILY RENEWAL CHECK REPORT")
        print("=" * 60)
        print(f"Timestamp: {results['timestamp']}")

        # Conversions
        conversions = results.get("conversions", [])
        print(f"\n--- CONVERSIONS DETECTED: {len(conversions)} ---")
        if conversions:
            for c in conversions:
                print(f"  {c['subscriber_id']}: {c['email']} (paid {c['payment_date']})")

        # Due reminders
        due = results.get("due_reminders", [])
        print(f"\n--- REMINDERS DUE: {len(due)} ---")
        if due:
            print(f"{'ID':<8} {'Name':<25} {'Email':<30} {'Reminder'}")
            print("-" * 75)
            for r in due:
                name = f"{r['name']} {r['last_name']}".strip()[:24]
                print(f"{r['subscriber_id']:<8} {name:<25} {r['email']:<30} #{r['reminder_num']}")

        # Stats
        stats = results.get("stats", {})
        print("\n--- TRACKING STATS ---")
        print(f"Total tracked:    {stats.get('total_tracked', 0)}")
        print(f"Pending:          {stats.get('pending', 0)}")
        print(f"Responded:        {stats.get('responded', 0)}")
        print(f"Converted:        {stats.get('converted', 0)}")
        print(f"Lapsed:           {stats.get('lapsed', 0)}")
        print(f"Reminder 1 sent:  {stats.get('reminder_1_sent', 0)}")
        print(f"Reminder 2 sent:  {stats.get('reminder_2_sent', 0)}")
        print(f"Reminder 3 sent:  {stats.get('reminder_3_sent', 0)}")

    def preview_emails(self, tracker: Optional[EmailTracker] = None) -> list:
        """
        Preview emails that would be sent.

        Args:
            tracker: Optional EmailTracker (creates new if not provided)

        Returns:
            List of dicts with contact info and email content
        """
        if tracker is None:
            tracker = EmailTracker()

        due = self.get_due_reminders(tracker)
        previews = []

        for contact in due:
            email_content = self.generate_email(contact)
            previews.append({
                "subscriber_id": contact["subscriber_id"],
                "email_address": contact["email"],
                "reminder_num": contact["reminder_num"],
                "email_content": email_content,
            })

        return previews


# Quick test when run directly
if __name__ == "__main__":
    workflow = EmailWorkflow()
    report = workflow.generate_renewal_report()
    workflow.print_candidate_list()
