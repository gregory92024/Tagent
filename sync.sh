#!/bin/bash
# TeachCE CRM Sync Script
# Syncs Kajabi orders to Excel and HubSpot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Set log file
LOG_FILE="logs/sync_$(date +%Y%m%d_%H%M%S).log"

echo "========================================" | tee -a "$LOG_FILE"
echo "TeachCE CRM Sync - $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Run sync based on argument
case "${1:-full}" in
    full)
        echo "Running full sync..." | tee -a "$LOG_FILE"
        python run.py 2>&1 | tee -a "$LOG_FILE"
        ;;
    kajabi)
        echo "Running Kajabi sync only..." | tee -a "$LOG_FILE"
        python run.py --kajabi-only 2>&1 | tee -a "$LOG_FILE"
        ;;
    hubspot)
        echo "Running HubSpot sync only..." | tee -a "$LOG_FILE"
        python run.py --hubspot-only 2>&1 | tee -a "$LOG_FILE"
        ;;
    setup)
        echo "Setting up HubSpot properties..." | tee -a "$LOG_FILE"
        python run.py --setup 2>&1 | tee -a "$LOG_FILE"
        ;;
    *)
        echo "Usage: $0 [full|kajabi|hubspot|setup]"
        echo "  full    - Full sync (Kajabi -> Excel -> HubSpot)"
        echo "  kajabi  - Kajabi to Excel only"
        echo "  hubspot - Excel to HubSpot only"
        echo "  setup   - Setup HubSpot custom properties"
        exit 1
        ;;
esac

echo "Sync completed at $(date)" | tee -a "$LOG_FILE"
echo "Log saved to: $LOG_FILE"
