# CRM Integration

Python-based integration that syncs customer data from Kajabi to HubSpot via an Excel master list.

## Data Flow

```
Kajabi Contacts → Excel Spreadsheet → HubSpot Contacts
```

**What this project does:**
- Syncs historical contact data from Kajabi to Excel (~1,770 records)
- Enriches HubSpot contacts with extended data (credentials, specialty, courses)
- Incremental sync - only processes changed contacts

**Related project:** The separate [Agent](../Agent/) (Node.js) handles new purchases and HubSpot Deal creation.

## Quick Start

```bash
# Navigate to project
cd /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration

# Activate virtual environment
source venv/bin/activate

# Run full sync
python run.py

# Or run specific stages
python run.py --kajabi-only    # Sync Kajabi → Excel only
python run.py --hubspot-only   # Sync Excel → HubSpot only
python run.py --setup          # Setup HubSpot custom properties

# Email renewal workflow
python run.py --renewal-status # Show renewal status summary
python run.py --renewal-list   # Show all renewal candidates
```

## File Structure

```
CRM_integration/
├── src/
│   ├── __init__.py           # Package init
│   ├── kajabi_client.py      # Kajabi API client (OAuth2)
│   ├── hubspot_client.py     # HubSpot API client
│   ├── excel_sync.py         # Excel read/write operations
│   ├── email_workflow.py     # Renewal candidate identification
│   └── sync_pipeline.py      # Main orchestration
├── data/
│   ├── sales_tracking.xlsx   # Master subscriber list
│   ├── last_sync.json        # Kajabi sync timestamp
│   └── hubspot_sync_state.json  # Contact sync hashes (auto-created)
├── logs/
│   ├── sync.log              # Operation logs
│   └── invalid_emails.log    # Invalid email tracking
├── run.py                    # CLI entry point
├── sync.sh                   # Bash automation wrapper
├── setup_cron.sh             # Cron job configuration
├── requirements.txt          # Python dependencies
├── .env                      # Credentials (gitignored)
├── .env.example              # Credential template
├── README.md                 # This file
├── CLAUDE.md                 # Project guidelines
├── CHANGELOG.md              # Version history
├── EMAIL_AUTOMATION_SETUP.md # Email automation configuration
├── EMAIL_SETUP_TODO.md       # Email setup tasks
├── EMAIL_WORKFLOW_SYSTEM.md  # Email workflow documentation
└── venv/                     # Python virtual environment
```

## Incremental Sync

The integration uses data hashing to detect changes and only sync modified contacts:

```
First Run:
  - Processes all contacts
  - Builds hubspot_sync_state.json with data hashes

Subsequent Runs:
  - Compares each contact's data hash
  - Only syncs contacts with changed data
  - Much faster than full sync
```

**Force full sync:**
```bash
# In Python
python -c "from src.sync_pipeline import SyncPipeline; SyncPipeline().sync_to_hubspot(force_full=True)"
```

**Reset sync state:**
```bash
rm data/hubspot_sync_state.json
python run.py --hubspot-only
```

## HubSpot Custom Properties

These custom contact properties are created automatically:

| Property | Description |
|----------|-------------|
| `credentials` | Professional credentials (MD, DO, DC, etc.) |
| `organization` | Practice or company name |
| `specialty` | Medical specialty |
| `year_acquired` | Year became a customer |
| `courses_ordered` | List of courses purchased |
| `subscriber_number` | Legacy subscriber ID |

## Environment Variables

Required in `.env`:
```
KAJABI_CLIENT_ID=...
KAJABI_CLIENT_SECRET=...
HUBSPOT_ACCESS_TOKEN=...
HUBSPOT_API_KEY=...
HUBSPOT_CLIENT_SECRET=...
```

## Scheduling

See [SYNC_RUN_ORDER.md](./SYNC_RUN_ORDER.md) for recommended run order between Agent and CRM_integration.

**Important:** Always run Agent first, then CRM_integration, to prevent Agent's basic contact data from overwriting enriched data.

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Project guidelines and rules
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[SYNC_RUN_ORDER.md](./SYNC_RUN_ORDER.md)** - Run order between projects

## Git Workflow

- **main:** Production branch (protected)
- **tim-dev:** Development branch (work here)
- **GitHub:** https://github.com/timothysepulvado/CRM_integration (private)

## Troubleshooting

### First run is slow
Expected. First run builds sync state by processing all contacts. Subsequent runs only sync changes.

### Invalid email errors
Check `logs/invalid_emails.log` for a list of invalid email addresses that were skipped.

### HubSpot rate limits
The integration includes built-in delays. If you hit rate limits, wait a few minutes and retry.

## Requirements

- Python 3.10+
- Active Kajabi account with API access
- HubSpot account with CRM access
- Valid API credentials in `.env`
