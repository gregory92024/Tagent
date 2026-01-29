# CRM Sync System - Run Order & Scheduling

## Overview

Two separate projects handle different aspects of your CRM sync:

| Project | Purpose | Data Flow | Docs |
|---------|---------|-----------|------|
| **Agent** (Node.js) | Kajabi purchases → HubSpot deals | Creates deals + basic contacts | [README](Agent/README.md) |
| **CRM_integration** (Python) | Excel master → HubSpot contacts | Enriches contacts with extended data | [README](CRM_integration/README.md) |

---

## Run Order (IMPORTANT)

**Always run Agent FIRST, then CRM_integration SECOND**

```
1. Agent       → Creates deals, creates/updates basic contacts
2. CRM_integration → Enriches contacts with address, credentials, courses, etc.
```

This prevents Agent's basic contact data from overwriting CRM_integration's richer data.

---

## Scheduling Recommendation

### Option A: Cron Jobs (Linux/WSL)
```bash
# Run Agent at 6:00 AM daily
0 6 * * * cd /mnt/c/Users/Gregory/OneDrive/Desktop/Agent && npm start >> /var/log/agent.log 2>&1

# Run CRM_integration at 7:00 AM daily (1 hour after Agent)
0 7 * * * cd /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration && source venv/bin/activate && python -m src.sync_pipeline >> /var/log/crm.log 2>&1
```

### Option B: Windows Task Scheduler
1. Agent: 6:00 AM → `npm start` in Agent folder
2. CRM_integration: 7:00 AM → `python -m src.sync_pipeline` in CRM_integration folder

---

## Efficiency Features Added

### Agent (Node.js)
- **Auto-advancing cutoff date**: After each sync, saves the latest purchase date
- **Next run**: Automatically skips already-processed purchases
- **Tracking file**: `sync_state.json`

### CRM_integration (Python)
- **Incremental HubSpot sync**: Only syncs new/changed contacts
- **Data hashing**: Detects changes by comparing contact data hashes
- **Tracking file**: `data/hubspot_sync_state.json`
- **First run**: Builds initial state (processes all contacts once)
- **Subsequent runs**: Only syncs contacts with changed data

---

## Manual Run Commands

### Agent
```bash
cd /mnt/c/Users/Gregory/OneDrive/Desktop/Agent
npm start
```

### CRM_integration
```bash
cd /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration
source venv/bin/activate
python -m src.sync_pipeline
```

### Force Full Sync (CRM_integration)
```python
# In Python, call with force_full=True
pipeline = SyncPipeline()
pipeline.sync_to_hubspot(force_full=True)
```

---

## Data Flow Summary

```
KAJABI API
    │
    ▼
┌─────────────────────────────────────────┐
│  AGENT (Node.js)                        │
│  • Fetches purchases from Kajabi        │
│  • Creates/updates basic contacts       │
│  • Creates deals (closedwon)            │
│  • Logs to sales_data.xlsx              │
│  • Saves sync state (auto-cutoff)       │
└─────────────────────────────────────────┘
    │
    ▼
HUBSPOT (contacts + deals)
    ▲
    │
┌─────────────────────────────────────────┐
│  CRM_INTEGRATION (Python)               │
│  • Reads from sales_tracking.xlsx       │
│  • Enriches contacts with extended data │
│  • Credentials, specialty, courses      │
│  • Incremental sync (only changes)      │
└─────────────────────────────────────────┘
    ▲
    │
EXCEL (sales_tracking.xlsx - master data)
```

---

## Tracking Files

| File | Project | Purpose |
|------|---------|---------|
| `Agent/sync_state.json` | Agent | Last processed purchase date |
| `Agent/sales_data.xlsx` | Agent | Log of all synced sales |
| `CRM_integration/data/last_sync.json` | CRM_integration | Last Kajabi sync time |
| `CRM_integration/data/hubspot_sync_state.json` | CRM_integration | Contact sync hashes |
| `CRM_integration/data/sales_tracking.xlsx` | CRM_integration | Master contact data |

---

## Troubleshooting

### Agent shows "No sales to process"
This is normal if no new Kajabi purchases since last sync. The cutoff auto-advances.

### CRM_integration first run is slow
Expected. First run builds sync state by processing all contacts. Subsequent runs are fast.

### To reset and re-sync everything

**Agent:**
```bash
rm /mnt/c/Users/Gregory/OneDrive/Desktop/Agent/sync_state.json
```

**CRM_integration:**
```bash
rm /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/data/hubspot_sync_state.json
```

---

## Documentation Links

### Agent (Node.js)
- [README.md](Agent/README.md) - Overview and quick start
- [SETUP.md](Agent/SETUP.md) - Detailed setup instructions
- [USAGE.md](Agent/USAGE.md) - Usage examples
- [API_DOCUMENTATION.md](Agent/API_DOCUMENTATION.md) - Technical reference
- [CHANGELOG.md](Agent/CHANGELOG.md) - Version history
- [STATUS.md](Agent/STATUS.md) - Current status

### CRM_integration (Python)
- [README.md](CRM_integration/README.md) - Overview and quick start
- [CLAUDE.md](CRM_integration/CLAUDE.md) - Project guidelines
- [CHANGELOG.md](CRM_integration/CHANGELOG.md) - Version history

---

**Last Updated:** 2026-01-27
