#!/usr/bin/env python3
"""
TeachCE CRM Integration - Main Entry Point

Usage:
    python run.py                    # Run full sync
    python run.py --setup            # Setup HubSpot properties only
    python run.py --kajabi-only      # Sync Kajabi to Excel only
    python run.py --hubspot-only     # Sync Excel to HubSpot only
    python run.py --renewal-status   # Show renewal status summary
    python run.py --renewal-list     # Show all renewal candidates
    python run.py --renewal-check    # Daily check: conversions + due reminders
    python run.py --renewal-send     # Preview emails ready to send
    python run.py --mark-sent ID     # Mark email as sent for subscriber
    python run.py --mark-response ID # Mark response received from subscriber
"""

import sys
import argparse
from src.sync_pipeline import SyncPipeline
from src.email_workflow import EmailWorkflow
from src.email_tracking import EmailTracker


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
    parser.add_argument(
        "--renewal-status", action="store_true", help="Show renewal status summary counts"
    )
    parser.add_argument(
        "--renewal-list", action="store_true", help="Show all renewal candidates with details"
    )
    parser.add_argument(
        "--renewal-check", action="store_true", help="Daily check: conversions + due reminders"
    )
    parser.add_argument(
        "--renewal-send", action="store_true", help="Preview emails ready to send"
    )
    parser.add_argument(
        "--mark-sent", type=str, metavar="ID", help="Mark email as sent for subscriber ID"
    )
    parser.add_argument(
        "--mark-response", type=str, metavar="ID", help="Mark response received from subscriber ID"
    )

    args = parser.parse_args()

    # Handle renewal workflow commands
    if args.renewal_status:
        workflow = EmailWorkflow()
        workflow.generate_renewal_report(verbose=True)
        return

    if args.renewal_list:
        workflow = EmailWorkflow()
        workflow.generate_renewal_report(verbose=True)
        workflow.print_candidate_list()
        return

    if args.renewal_check:
        workflow = EmailWorkflow()
        # Run daily check (without Kajabi conversion check for now)
        results = workflow.run_daily_check(kajabi_client=None)
        workflow.print_daily_check_report(results)
        return

    if args.renewal_send:
        workflow = EmailWorkflow()
        tracker = EmailTracker()
        previews = workflow.preview_emails(tracker)

        print("\n" + "=" * 60)
        print("EMAILS READY TO SEND")
        print("=" * 60)

        if not previews:
            print("No emails due at this time.")
        else:
            for i, p in enumerate(previews, 1):
                print(f"\n--- Email #{i} (Reminder {p['reminder_num']}) ---")
                print(f"To: {p['email_address']}")
                print(f"Subscriber ID: {p['subscriber_id']}")
                print("-" * 40)
                # Show first 500 chars of email content
                content = p['email_content'][:500]
                if len(p['email_content']) > 500:
                    content += "\n... [truncated]"
                print(content)
                print()

            print(f"\nTotal: {len(previews)} emails ready to send")
            print("Use --mark-sent <ID> after sending each email manually")
        return

    if args.mark_sent:
        tracker = EmailTracker()
        subscriber_id = args.mark_sent

        # Get current status to determine which reminder to mark
        contact = tracker.get_contact_status(subscriber_id)

        if contact is None:
            print(f"Error: Subscriber {subscriber_id} not found in tracking")
            sys.exit(1)

        next_reminder = tracker.get_next_reminder_num(subscriber_id)

        if next_reminder is None:
            print(f"Subscriber {subscriber_id}: All reminders already sent or contact not pending")
            return

        if tracker.record_email_sent(subscriber_id, next_reminder):
            print(f"Marked reminder {next_reminder} as sent for subscriber {subscriber_id}")
        else:
            print(f"Error: Could not mark email sent for {subscriber_id}")
            sys.exit(1)
        return

    if args.mark_response:
        tracker = EmailTracker()
        subscriber_id = args.mark_response

        if tracker.record_response(subscriber_id):
            print(f"Marked response received for subscriber {subscriber_id}")
        else:
            print(f"Error: Subscriber {subscriber_id} not found in tracking")
            sys.exit(1)
        return

    # Handle sync commands
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
