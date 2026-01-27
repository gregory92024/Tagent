#!/bin/bash
# Setup cron job for TeachCE CRM Sync on WSL/Linux
# This replaces the macOS LaunchAgent (com.teachce.crm-sync.plist)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync.sh"

echo "TeachCE CRM Sync - Cron Setup"
echo "=============================="
echo ""
echo "Script location: $SYNC_SCRIPT"
echo ""

# Check if cron service is running
if ! pgrep -x "cron" > /dev/null; then
    echo "WARNING: Cron service is not running."
    echo "To start cron in WSL, run: sudo service cron start"
    echo ""
fi

# Show current crontab
echo "Current crontab:"
crontab -l 2>/dev/null || echo "(empty)"
echo ""

# Ask user what schedule they want
echo "Select a schedule for the sync job:"
echo "1) Daily at 6:00 AM (recommended)"
echo "2) Twice daily (6 AM and 6 PM)"
echo "3) Every hour"
echo "4) Weekly on Monday at 9 AM"
echo "5) Custom (manual entry)"
echo "6) Remove existing TeachCE cron job"
echo "7) Cancel"
echo ""
read -p "Enter choice [1-7]: " choice

case $choice in
    1)
        CRON_SCHEDULE="0 6 * * *"
        ;;
    2)
        CRON_SCHEDULE="0 6,18 * * *"
        ;;
    3)
        CRON_SCHEDULE="0 * * * *"
        ;;
    4)
        CRON_SCHEDULE="0 9 * * 1"
        ;;
    5)
        read -p "Enter cron schedule (e.g., '0 6 * * *'): " CRON_SCHEDULE
        ;;
    6)
        # Remove existing job
        crontab -l 2>/dev/null | grep -v "CRM_integration/sync.sh" | crontab -
        echo "Removed TeachCE cron job."
        exit 0
        ;;
    7)
        echo "Cancelled."
        exit 0
        ;;
    *)
        echo "Invalid choice."
        exit 1
        ;;
esac

# Create new crontab entry
CRON_LINE="$CRON_SCHEDULE $SYNC_SCRIPT full >> $SCRIPT_DIR/logs/cron.log 2>&1"

# Add to crontab (preserving existing entries, removing old TeachCE jobs)
(crontab -l 2>/dev/null | grep -v "CRM_integration/sync.sh"; echo "$CRON_LINE") | crontab -

echo ""
echo "Cron job installed:"
echo "  Schedule: $CRON_SCHEDULE"
echo "  Command: $SYNC_SCRIPT full"
echo "  Log: $SCRIPT_DIR/logs/cron.log"
echo ""
echo "To verify, run: crontab -l"
echo ""
echo "Make sure cron service is running:"
echo "  sudo service cron start"
echo "  sudo service cron status"
