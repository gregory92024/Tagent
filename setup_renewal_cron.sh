#!/bin/bash
# Setup Renewal Cron Job
# Adds daily renewal check to crontab

SCRIPT_DIR="/mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration"
CRON_SCRIPT="$SCRIPT_DIR/renewal_cron.sh"

# Make the cron script executable
chmod +x "$CRON_SCRIPT"

echo "Setting up daily renewal check cron job..."
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "renewal_cron.sh"; then
    echo "Renewal cron job already exists in crontab."
    echo ""
    echo "Current crontab entries:"
    crontab -l | grep renewal
else
    # Add cron job - runs daily at 6:00 AM
    (crontab -l 2>/dev/null; echo "0 6 * * * $CRON_SCRIPT") | crontab -
    echo "Added cron job to run daily at 6:00 AM"
fi

echo ""
echo "Cron setup complete!"
echo ""
echo "To view all cron jobs: crontab -l"
echo "To edit cron jobs: crontab -e"
echo "To remove this cron job: crontab -l | grep -v renewal_cron | crontab -"
echo ""
echo "Manual test: ./renewal_cron.sh"
echo "View logs: cat logs/renewal_cron.log"
