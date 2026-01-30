"""
Email Workflow Module
Identifies renewal candidates and manages email workflow logic
"""

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional
import pandas as pd

from .excel_sync import ExcelSync


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


# Quick test when run directly
if __name__ == "__main__":
    workflow = EmailWorkflow()
    report = workflow.generate_renewal_report()
    workflow.print_candidate_list()
