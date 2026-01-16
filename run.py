#!/usr/bin/env python3
"""
TeachCE CRM Integration - Main Entry Point

Usage:
    python run.py                    # Run full sync
    python run.py --setup            # Setup HubSpot properties only
    python run.py --kajabi-only      # Sync Kajabi to Excel only
    python run.py --hubspot-only     # Sync Excel to HubSpot only
"""

import sys
import argparse
from src.sync_pipeline import SyncPipeline


def main():
    parser = argparse.ArgumentParser(
        description="TeachCE CRM Integration - Sync Kajabi to HubSpot"
    )
    parser.add_argument(
        "--setup", action="store_true", help="Setup HubSpot custom properties only"
    )
    parser.add_argument(
        "--kajabi-only", action="store_true", help="Sync Kajabi to Excel only"
    )
    parser.add_argument(
        "--hubspot-only", action="store_true", help="Sync Excel to HubSpot only"
    )

    args = parser.parse_args()

    pipeline = SyncPipeline()

    if args.setup:
        print("Setting up HubSpot custom properties...")
        pipeline.setup_hubspot_properties()
        print("Done!")

    elif args.kajabi_only:
        print("Syncing Kajabi orders to Excel...")
        results = pipeline.sync_kajabi_orders()
        print(f"Results: {results}")

    elif args.hubspot_only:
        print("Syncing Excel to HubSpot...")
        pipeline.excel.load_spreadsheet()
        results = pipeline.sync_to_hubspot()
        print(f"Results: {results}")

    else:
        print("Running full sync pipeline...")
        results = pipeline.run_full_sync()
        print(f"\nFinal Results: {results}")


if __name__ == "__main__":
    main()
