#!/bin/bash
# Daily Renewal Check Cron Script
# Runs the renewal workflow check and logs results

# Change to project directory
cd /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration

# Ensure logs directory exists
mkdir -p logs

# Activate virtual environment
source venv/bin/activate

# Run renewal check and append to log
echo "========================================" >> logs/renewal_cron.log
echo "Renewal Check: $(date)" >> logs/renewal_cron.log
echo "========================================" >> logs/renewal_cron.log
python run.py --renewal-check >> logs/renewal_cron.log 2>&1

# Log completion
echo "Completed: $(date)" >> logs/renewal_cron.log
echo "" >> logs/renewal_cron.log

# Deactivate venv
deactivate
