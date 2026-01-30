# CRM Integration - Project Rules

## Project Overview

This is a Python-based CRM integration that syncs customer data from Kajabi to HubSpot via an Excel master list.

**Pipeline:**
```
Kajabi Contacts → Excel Spreadsheet → HubSpot Contacts
```

**Related Project:** A separate Node.js project (`Desktop/Agent/`) handles new purchases and HubSpot Deal creation. That project filters for purchases after Jan 5, 2026 and creates both Contacts and Deals.

**This project's scope:** Historical contact synchronization from the master Excel list (~1,770 records).

---

## Git Workflow

- **main:** Production branch. Always stable and working.
- **tim-dev:** Development branch. All changes go here first.
- **GitHub:** https://github.com/timothysepulvado/CRM_integration (private)

**Rules:**
1. Never commit directly to main
2. Always work on tim-dev branch
3. Test changes before merging to main

---

## API Credentials

**CRITICAL: Never commit `.env` file to git**

Required environment variables in `.env`:
```
KAJABI_CLIENT_ID=...
KAJABI_CLIENT_SECRET=...
HUBSPOT_ACCESS_TOKEN=...
HUBSPOT_API_KEY=...
HUBSPOT_CLIENT_SECRET=...
```

The `.env` file is already in `.gitignore`.

---

## File Structure

```
CRM_integration/
├── .env                    # API credentials (DO NOT COMMIT)
├── requirements.txt        # Python dependencies
├── run.py                  # CLI entry point
├── sync.sh                 # Bash automation wrapper
├── setup_cron.sh           # Cron job setup for WSL
├── README.md               # Main documentation
├── CHANGELOG.md            # Version history
├── data/
│   ├── sales_tracking.xlsx # Master subscriber list
│   ├── last_sync.json      # Last sync timestamp
│   └── hubspot_sync_state.json  # Contact sync hashes (auto-created)
├── logs/
│   ├── sync.log            # Operation logs
│   └── invalid_emails.log  # Invalid email addresses
└── src/
    ├── kajabi_client.py    # Kajabi API (OAuth2, contacts, purchases)
    ├── hubspot_client.py   # HubSpot API (contacts, custom properties)
    ├── excel_sync.py       # Excel read/write operations
    ├── email_workflow.py   # Renewal candidate identification
    └── sync_pipeline.py    # Main orchestration + incremental sync
```

---

## How to Run

**Prerequisites:**
```bash
cd /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration
source venv/bin/activate
```

**Commands:**
```bash
python run.py                  # Full sync (Kajabi → Excel → HubSpot)
python run.py --setup          # Setup HubSpot custom properties only
python run.py --kajabi-only    # Sync Kajabi to Excel only
python run.py --hubspot-only   # Sync Excel to HubSpot only
python run.py --renewal-status # Show renewal status summary
python run.py --renewal-list   # Show all renewal candidates
```

**Automation:**
```bash
./sync.sh                      # Run via bash wrapper
./setup_cron.sh                # Configure cron schedule
```

---

## Code Style

- Python 3.10+
- Use type hints for function parameters and returns
- Use docstrings for classes and public methods
- Follow existing patterns in the codebase
- Log all API operations to `logs/sync.log`

---

## HubSpot Custom Properties

These custom contact properties are created automatically:
- `credentials` - Professional credentials (MD, DO, DC, etc.)
- `organization` - Practice or company name
- `specialty` - Medical specialty
- `year_acquired` - Year became a customer
- `courses_ordered` - List of courses purchased
- `subscriber_number` - Legacy subscriber ID

---

## Incremental Sync Mechanism

The HubSpot sync uses data hashing to detect changes:

**How it works:**
1. Each contact's data is hashed using `_compute_contact_hash()`
2. Hashes are stored in `data/hubspot_sync_state.json`
3. On subsequent runs, only contacts with changed hashes are synced

**Key functions in `sync_pipeline.py`:**
- `_compute_contact_hash()` - Creates MD5 hash of contact data
- `_load_hubspot_sync_state()` - Loads stored hashes
- `_save_hubspot_sync_state()` - Saves hashes after sync
- `_is_contact_changed()` - Checks if contact needs sync
- `_mark_contact_synced()` - Records synced contact hash

**Force full sync:**
```python
pipeline.sync_to_hubspot(force_full=True)
```

**Reset incremental state:**
```bash
rm data/hubspot_sync_state.json
```

---

## Error Handling

- Invalid emails are logged to `logs/invalid_emails.log`
- Individual record failures don't stop the entire sync
- All errors are logged with timestamps to `logs/sync.log`

---

## Testing

Before merging to main:
1. Run `python run.py --hubspot-only` to test contact sync
2. Check `logs/sync.log` for errors
3. Verify a sample of contacts in HubSpot UI

---

## Documentation

- **[README.md](README.md)** - Main documentation and quick start
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[SYNC_RUN_ORDER.md](./SYNC_RUN_ORDER.md)** - Run order between projects
- **[Agent README](../Agent/README.md)** - Related Node.js project
