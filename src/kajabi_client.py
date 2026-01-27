"""
Kajabi API Client
Handles authentication and fetching orders from Kajabi
"""

import os
import requests
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class KajabiClient:
    """Client for interacting with Kajabi API"""

    BASE_URL = "https://api.kajabi.com/v1"

    def __init__(self):
        self.client_id = os.getenv("KAJABI_CLIENT_ID")
        self.client_secret = os.getenv("KAJABI_CLIENT_SECRET")
        self.access_token = None
        self._validate_credentials()

    def _validate_credentials(self):
        """Ensure credentials are set"""
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "KAJABI_CLIENT_ID and KAJABI_CLIENT_SECRET must be set in .env"
            )

    def authenticate(self) -> str:
        """
        Authenticate with Kajabi OAuth2 and get access token
        Returns the access token
        """
        # Correct endpoint: api.kajabi.com/v1/oauth/token
        auth_url = "https://api.kajabi.com/v1/oauth/token"

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(auth_url, data=payload)
        response.raise_for_status()

        data = response.json()
        self.access_token = data.get("access_token")
        return self.access_token

    def _get_headers(self) -> dict:
        """Get authorization headers"""
        if not self.access_token:
            self.authenticate()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def get_orders(self, since: Optional[datetime] = None, limit: int = 100) -> list:
        """
        Fetch purchases from Kajabi (uses /purchases endpoint)

        Args:
            since: Only fetch orders after this date
            limit: Maximum number of orders to fetch

        Returns:
            List of normalized order dictionaries
        """
        endpoint = f"{self.BASE_URL}/purchases"
        params = {"per_page": limit}

        if since:
            params["filter[created_at_after]"] = since.isoformat()

        response = requests.get(
            endpoint, headers=self._get_headers(), params=params
        )
        response.raise_for_status()

        # Parse JSON:API format and normalize
        data = response.json().get("data", [])
        return [self._normalize_purchase(item) for item in data]

    def _normalize_purchase(self, item: dict) -> dict:
        """Convert JSON:API purchase format to flat dict"""
        attrs = item.get("attributes", {})
        relationships = item.get("relationships", {})

        return {
            "id": item.get("id"),
            "amount": attrs.get("amount_in_cents", 0) / 100,
            "currency": attrs.get("currency"),
            "created_at": attrs.get("created_at"),
            "payment_type": attrs.get("payment_type"),
            "customer_id": relationships.get("customer", {}).get("data", {}).get("id"),
            "offer_id": relationships.get("offer", {}).get("data", {}).get("id"),
        }

    def get_offers(self) -> list:
        """Fetch all offers/courses from Kajabi"""
        endpoint = f"{self.BASE_URL}/offers"

        response = requests.get(endpoint, headers=self._get_headers())
        response.raise_for_status()

        data = response.json().get("data", [])
        return [self._normalize_offer(item) for item in data]

    def _normalize_offer(self, item: dict) -> dict:
        """Convert JSON:API offer format to flat dict"""
        attrs = item.get("attributes", {})
        return {
            "id": item.get("id"),
            "title": attrs.get("title"),
            "description": attrs.get("description"),
            "price": attrs.get("price_in_cents", 0) / 100 if attrs.get("price_in_cents") else None,
            "created_at": attrs.get("created_at"),
        }

    def get_contacts(self, limit: int = 100) -> list:
        """Fetch contacts/subscribers from Kajabi"""
        endpoint = f"{self.BASE_URL}/contacts"
        params = {"per_page": limit}

        response = requests.get(
            endpoint, headers=self._get_headers(), params=params
        )
        response.raise_for_status()

        data = response.json().get("data", [])
        return [self._normalize_contact(item) for item in data]

    def _normalize_contact(self, item: dict) -> dict:
        """Convert JSON:API contact format to flat dict for Excel/HubSpot sync"""
        attrs = item.get("attributes", {})

        # Split name into first/last
        full_name = attrs.get("name", "")
        name_parts = full_name.split(" ", 1) if full_name else ["", ""]
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        return {
            "id": item.get("id"),
            "name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "email": attrs.get("email"),
            "phone": attrs.get("phone_number"),
            "billing_street": attrs.get("address_line_1"),
            "billing_city": attrs.get("address_city"),
            "billing_province": attrs.get("address_state"),
            "billing_zip": attrs.get("address_zip"),
            "created_at": attrs.get("created_at"),
        }


# Quick test when run directly
if __name__ == "__main__":
    client = KajabiClient()
    print("Authenticating with Kajabi...")
    token = client.authenticate()
    print(f"Got access token: {token[:20]}...")

    print("\nFetching orders...")
    orders = client.get_orders(limit=5)
    print(f"Found {len(orders)} orders")
