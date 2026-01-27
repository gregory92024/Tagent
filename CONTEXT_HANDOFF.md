# Context Handoff - CRM Integration

> **ARCHIVED:** This document has been superseded by [README.md](README.md).
> Kept for historical reference only.

**Last Updated:** 2026-01-24
**Archived:** 2026-01-27
**Branch:** tim-dev (safe dev branch, main is protected)

---

## PROJECT STATUS: COMPLETE

All core functionality is implemented and working.

---

## WHAT THE PIPELINE DOES

```
Kajabi Contacts → Excel Spreadsheet → HubSpot CONTACTS
```

**What we sync:** Customer info (name, email, phone, address, courses ordered)
**What we DON'T sync:** Purchases as Deals (handled by separate Agent project)

---

## TWO INTEGRATION PROJECTS

| Project | Location | Purpose |
|---------|----------|---------|
| **CRM_integration** (Python) | `Desktop/CRM_integration/` | Historical master list → HubSpot Contacts |
| **Agent** (Node.js) | `Desktop/Agent/` | New purchases → Contacts + Deals |

**Agent project:**
- GitHub: `github.com/gregory92024/Tagent`
- Filters: Only purchases after Jan 5, 2026
- Creates HubSpot Deals (223 exist)

---

## COMPLETED FEATURES

| Component | Status |
|-----------|--------|
| Kajabi OAuth2 | Working |
| Kajabi → Excel sync | Working (1,770 records) |
| Excel → HubSpot contacts | Working |
| Full pipeline | Working |
| Email validation | Added (logs invalid emails) |
| Bash wrapper | Working |
| Cron service | Running |
| CLAUDE.md | Created |

---

## FILE LOCATIONS

```
/mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/
├── src/
│   ├── kajabi_client.py    # Kajabi API (auth, purchases, contacts, offers)
│   ├── hubspot_client.py   # HubSpot API (contacts, custom properties)
│   ├── excel_sync.py       # Excel operations
│   └── sync_pipeline.py    # Main orchestration + email validation
├── data/
│   ├── sales_tracking.xlsx # Master subscriber list
│   └── last_sync.json      # Last sync timestamp
├── logs/
│   ├── sync.log            # Operation logs
│   └── invalid_emails.log  # Invalid email addresses
├── run.py                  # CLI entry point
├── sync.sh                 # Automation wrapper
├── setup_cron.sh           # WSL cron job setup
├── CLAUDE.md               # Project rules
├── SETUP_PLAN.md           # Full documentation
└── .env                    # API credentials (not in git)
```

---

## GIT STATUS

- **main branch:** Production, working, protected
- **tim-dev branch:** Development, currently checked out
- **GitHub:** https://github.com/timothysepulvado/CRM_integration (private)

---

## HOW TO RUN

```bash
cd /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration
source venv/bin/activate
python run.py                  # Full sync
python run.py --hubspot-only   # Sync Excel to HubSpot only
python run.py --kajabi-only    # Sync Kajabi to Excel only
```

---

## CREDENTIALS (in .env, not in git)

- KAJABI_CLIENT_ID, KAJABI_CLIENT_SECRET
- HUBSPOT_ACCESS_TOKEN, HUBSPOT_API_KEY, HUBSPOT_CLIENT_SECRET

---

## OPTIONAL FUTURE ENHANCEMENTS

1. **Configure cron schedule** - Run `./setup_cron.sh` when ready for automated syncs
2. **Auto-fix common email issues** - Extend validation to suggest/apply fixes
