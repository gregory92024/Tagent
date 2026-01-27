"""
Excel Sync Module
Handles reading and updating the master subscriber spreadsheet
"""

import os
from datetime import datetime
from typing import Optional
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class ExcelSync:
    """Handles Excel spreadsheet operations for subscriber tracking"""

    # Column mapping from Kajabi to Excel
    KAJABI_TO_EXCEL_MAP = {
        "name": "Name",  # Will need to split into Name + Last Name
        "email": "Email",
        "billing_street": "Street Address",
        "billing_city": "City",
        "billing_province": "St",
        "billing_zip": "Zip",
        "phone": "Phone",
        "lineitem_name": "Courses Ordered",  # Append to existing
        "created_at": "Year Acquired",  # Extract year
        "total": "Payment",
    }

    # Expected Excel columns
    EXCEL_COLUMNS = [
        "#Subscribers",
        "Name",
        "Last Name",
        "Credentials",
        "Organization",
        "Street Address",
        "City",
        "St",
        "Zip",
        "Specialty",
        "Year Acquired",
        "Start",
        "Payment",
        "Phone",
        "Fax",
        "Email",
        "Email 2",
        "Courses Ordered",
    ]

    def __init__(self, spreadsheet_path: Optional[str] = None):
        self.spreadsheet_path = spreadsheet_path or os.getenv(
            "SALES_SPREADSHEET_PATH", "./data/sales_tracking.xlsx"
        )
        self.df = None

    def load_spreadsheet(self) -> pd.DataFrame:
        """Load the Excel spreadsheet into a DataFrame"""
        try:
            self.df = pd.read_excel(self.spreadsheet_path)
            print(f"Loaded {len(self.df)} rows from {self.spreadsheet_path}")
            return self.df
        except FileNotFoundError:
            print(f"Spreadsheet not found: {self.spreadsheet_path}")
            print("Creating new spreadsheet with empty columns...")
            self.df = pd.DataFrame(columns=self.EXCEL_COLUMNS)
            return self.df

    def save_spreadsheet(self) -> bool:
        """Save the DataFrame back to Excel"""
        try:
            self.df.to_excel(self.spreadsheet_path, index=False)
            print(f"Saved {len(self.df)} rows to {self.spreadsheet_path}")
            return True
        except Exception as e:
            print(f"Error saving spreadsheet: {e}")
            return False

    def find_by_email(self, email: str) -> Optional[int]:
        """
        Find a subscriber by email address

        Returns:
            Row index if found, None otherwise
        """
        if self.df is None:
            self.load_spreadsheet()

        # Check both Email and Email 2 columns
        email_lower = email.lower()
        matches = self.df[
            (self.df["Email"].str.lower() == email_lower)
            | (self.df["Email 2"].str.lower() == email_lower)
        ]

        if not matches.empty:
            return matches.index[0]
        return None

    def add_subscriber(self, subscriber_data: dict) -> int:
        """
        Add a new subscriber to the spreadsheet

        Args:
            subscriber_data: Dict with subscriber info

        Returns:
            New row index
        """
        if self.df is None:
            self.load_spreadsheet()

        # Generate new subscriber number
        max_num = self.df["#Subscribers"].max()
        new_num = (max_num + 1) if pd.notna(max_num) else 1

        # Build new row
        new_row = {
            "#Subscribers": new_num,
            "Name": subscriber_data.get("first_name", ""),
            "Last Name": subscriber_data.get("last_name", ""),
            "Credentials": subscriber_data.get("credentials", ""),
            "Organization": subscriber_data.get("organization", ""),
            "Street Address": subscriber_data.get("address", ""),
            "City": subscriber_data.get("city", ""),
            "St": subscriber_data.get("state", ""),
            "Zip": subscriber_data.get("zip", ""),
            "Specialty": subscriber_data.get("specialty", ""),
            "Year Acquired": subscriber_data.get("year_acquired", datetime.now().year),
            "Start": subscriber_data.get("start_date", datetime.now().strftime("%Y-%m-%d")),
            "Payment": subscriber_data.get("payment", ""),
            "Phone": subscriber_data.get("phone", ""),
            "Fax": subscriber_data.get("fax", ""),
            "Email": subscriber_data.get("email", ""),
            "Email 2": subscriber_data.get("email_2", ""),
            "Courses Ordered": subscriber_data.get("courses_ordered", ""),
        }

        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        print(f"Added new subscriber #{new_num}: {subscriber_data.get('email')}")

        return len(self.df) - 1

    def update_subscriber(self, row_index: int, updates: dict) -> bool:
        """
        Update an existing subscriber

        Args:
            row_index: Index of the row to update
            updates: Dict with fields to update

        Returns:
            True if updated successfully
        """
        if self.df is None:
            self.load_spreadsheet()

        try:
            for field, value in updates.items():
                if field in self.df.columns and value is not None:
                    self.df.at[row_index, field] = value
            return True
        except Exception as e:
            print(f"Error updating subscriber at row {row_index}: {e}")
            return False

    def append_course(self, row_index: int, course_name: str) -> bool:
        """
        Append a course to a subscriber's Courses Ordered field

        Args:
            row_index: Index of the subscriber row
            course_name: Name of the course to add

        Returns:
            True if appended successfully
        """
        if self.df is None:
            self.load_spreadsheet()

        try:
            current_courses = self.df.at[row_index, "Courses Ordered"]

            if pd.isna(current_courses) or current_courses == "":
                self.df.at[row_index, "Courses Ordered"] = course_name
            else:
                # Check if course already exists
                if course_name not in str(current_courses):
                    self.df.at[row_index, "Courses Ordered"] = (
                        f"{current_courses}, {course_name}"
                    )
                else:
                    print(f"Course '{course_name}' already recorded")
                    return True

            print(f"Appended course '{course_name}' to row {row_index}")
            return True

        except Exception as e:
            print(f"Error appending course: {e}")
            return False

    def process_kajabi_order(self, order: dict) -> dict:
        """
        Process a Kajabi order and add/update subscriber

        Args:
            order: Kajabi order data

        Returns:
            Dict with result info
        """
        email = order.get("email", "").lower()
        if not email:
            return {"status": "error", "message": "No email in order"}

        # Parse name
        full_name = order.get("name", "")
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Extract year from created_at
        created_at = order.get("created_at", "")
        year_acquired = datetime.now().year
        if created_at:
            try:
                year_acquired = datetime.fromisoformat(created_at).year
            except (ValueError, TypeError):
                pass

        subscriber_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "address": order.get("billing_street", ""),
            "city": order.get("billing_city", ""),
            "state": order.get("billing_province", ""),
            "zip": order.get("billing_zip", ""),
            "phone": order.get("phone", ""),
            "year_acquired": year_acquired,
            "payment": order.get("total", ""),
            "courses_ordered": order.get("lineitem_name", ""),
        }

        # Check if subscriber exists
        existing_row = self.find_by_email(email)

        if existing_row is not None:
            # Append course to existing subscriber
            course_name = order.get("lineitem_name", "")
            if course_name:
                self.append_course(existing_row, course_name)
            return {"status": "updated", "row": existing_row, "email": email}
        else:
            # Add new subscriber
            new_row = self.add_subscriber(subscriber_data)
            return {"status": "created", "row": new_row, "email": email}

    def get_all_subscribers(self) -> list:
        """
        Get all subscribers as list of dicts

        Returns:
            List of subscriber dictionaries
        """
        if self.df is None:
            self.load_spreadsheet()

        return self.df.to_dict("records")


# Quick test when run directly
if __name__ == "__main__":
    sync = ExcelSync()
    sync.load_spreadsheet()
    print(f"\nColumns: {list(sync.df.columns)}")
    print(f"Total subscribers: {len(sync.df)}")
