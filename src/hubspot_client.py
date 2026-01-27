"""
HubSpot API Client
Handles contact creation, updates, and custom property management
"""

import os
import math
from typing import Optional
from dotenv import load_dotenv
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, SimplePublicObjectInput
from hubspot.crm.properties import PropertyCreate


def is_nan(value):
    """Check if value is NaN (handles both float NaN and pandas NaN)"""
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False

load_dotenv()


class HubSpotClient:
    """Client for interacting with HubSpot CRM API"""

    # Custom properties for TeachCE
    CUSTOM_PROPERTIES = [
        {
            "name": "credentials",
            "label": "Credentials",
            "type": "string",
            "field_type": "text",
            "group_name": "contactinformation",
            "description": "Professional credentials (MD, DO, DC, etc.)",
        },
        {
            "name": "organization",
            "label": "Organization",
            "type": "string",
            "field_type": "text",
            "group_name": "contactinformation",
            "description": "Practice or company name",
        },
        {
            "name": "specialty",
            "label": "Specialty",
            "type": "string",
            "field_type": "text",
            "group_name": "contactinformation",
            "description": "Medical specialty",
        },
        {
            "name": "year_acquired",
            "label": "Year Acquired",
            "type": "number",
            "field_type": "number",
            "group_name": "contactinformation",
            "description": "Year became a customer",
        },
        {
            "name": "courses_ordered",
            "label": "Courses Ordered",
            "type": "string",
            "field_type": "textarea",
            "group_name": "contactinformation",
            "description": "List of courses purchased",
        },
        {
            "name": "subscriber_number",
            "label": "Subscriber Number",
            "type": "number",
            "field_type": "number",
            "group_name": "contactinformation",
            "description": "Legacy subscriber ID number",
        },
    ]

    def __init__(self):
        self.access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
        self._validate_credentials()
        self.client = HubSpot(access_token=self.access_token)

    def _validate_credentials(self):
        """Ensure credentials are set"""
        if not self.access_token:
            raise ValueError("HUBSPOT_ACCESS_TOKEN must be set in .env")

    def create_custom_properties(self) -> dict:
        """
        Create custom contact properties in HubSpot
        Returns dict of created/existing properties
        """
        results = {"created": [], "existing": [], "errors": []}

        for prop in self.CUSTOM_PROPERTIES:
            try:
                property_create = PropertyCreate(
                    name=prop["name"],
                    label=prop["label"],
                    type=prop["type"],
                    field_type=prop["field_type"],
                    group_name=prop["group_name"],
                    description=prop["description"],
                )

                self.client.crm.properties.core_api.create(
                    object_type="contacts", property_create=property_create
                )
                results["created"].append(prop["name"])
                print(f"Created property: {prop['name']}")

            except Exception as e:
                if "already exists" in str(e).lower() or "409" in str(e):
                    results["existing"].append(prop["name"])
                    print(f"Property already exists: {prop['name']}")
                else:
                    results["errors"].append({"name": prop["name"], "error": str(e)})
                    print(f"Error creating {prop['name']}: {e}")

        return results

    def search_contact_by_email(self, email: str) -> Optional[dict]:
        """
        Search for a contact by email address
        Returns contact dict or None if not found
        """
        try:
            filter_group = {
                "filters": [
                    {
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email,
                    }
                ]
            }

            search_request = {
                "filterGroups": [filter_group],
                "properties": [
                    "email",
                    "firstname",
                    "lastname",
                    "credentials",
                    "specialty",
                    "courses_ordered",
                ],
            }

            response = self.client.crm.contacts.search_api.do_search(
                public_object_search_request=search_request
            )

            if response.results:
                return response.results[0].to_dict()
            return None

        except Exception as e:
            print(f"Error searching for contact {email}: {e}")
            return None

    def create_contact(self, contact_data: dict) -> Optional[str]:
        """
        Create a new contact in HubSpot

        Args:
            contact_data: Dict with contact properties

        Returns:
            Contact ID if created, None on error
        """
        try:
            properties = {
                "email": contact_data.get("email"),
                "firstname": contact_data.get("firstname"),
                "lastname": contact_data.get("lastname"),
                "phone": contact_data.get("phone"),
                "address": contact_data.get("address"),
                "city": contact_data.get("city"),
                "state": contact_data.get("state"),
                "zip": contact_data.get("zip"),
                # Custom properties
                "credentials": contact_data.get("credentials"),
                "organization": contact_data.get("organization"),
                "specialty": contact_data.get("specialty"),
                "year_acquired": contact_data.get("year_acquired"),
                "courses_ordered": contact_data.get("courses_ordered"),
                "subscriber_number": contact_data.get("subscriber_number"),
            }

            # Remove None and NaN values
            properties = {k: v for k, v in properties.items() if not is_nan(v)}

            simple_public_object_input = SimplePublicObjectInputForCreate(properties=properties)
            response = self.client.crm.contacts.basic_api.create(
                simple_public_object_input_for_create=simple_public_object_input
            )

            print(f"Created contact: {contact_data.get('email')}")
            return response.id

        except Exception as e:
            print(f"Error creating contact: {e}")
            return None

    def update_contact(self, contact_id: str, contact_data: dict) -> bool:
        """
        Update an existing contact in HubSpot

        Args:
            contact_id: HubSpot contact ID
            contact_data: Dict with properties to update

        Returns:
            True if updated, False on error
        """
        try:
            properties = {k: v for k, v in contact_data.items() if not is_nan(v)}

            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            self.client.crm.contacts.basic_api.update(
                contact_id=contact_id,
                simple_public_object_input=simple_public_object_input,
            )

            print(f"Updated contact ID: {contact_id}")
            return True

        except Exception as e:
            print(f"Error updating contact {contact_id}: {e}")
            return False

    def upsert_contact(self, contact_data: dict) -> Optional[str]:
        """
        Create or update a contact based on email

        Args:
            contact_data: Dict with contact properties (must include email)

        Returns:
            Contact ID
        """
        email = contact_data.get("email")
        if not email:
            print("Error: email is required for upsert")
            return None

        existing = self.search_contact_by_email(email)

        if existing:
            contact_id = existing.get("id")
            self.update_contact(contact_id, contact_data)
            return contact_id
        else:
            return self.create_contact(contact_data)


# Quick test when run directly
if __name__ == "__main__":
    client = HubSpotClient()
    print("HubSpot client initialized")

    print("\nCreating custom properties...")
    results = client.create_custom_properties()
    print(f"Results: {results}")
