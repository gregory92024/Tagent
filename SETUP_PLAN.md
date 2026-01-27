# TeachCE CRM Integration Setup Plan

**Created:** 2026-01-15
**Status:** In Progress
**Location:** `/mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration`

---

## Overview

Integrate Kajabi (course sales) with HubSpot (CRM) while maintaining an Excel master spreadsheet of all subscribers/customers.

### Data Flow
```
Kajabi API ──→ Python Script ──→ Excel Master List
                    │
                    └──────────→ HubSpot Contacts
```

---

## Credentials (Stored in .env)

| Service | Credentials | Status |
|---------|-------------|--------|
| Kajabi | Client ID, Client Secret | ✅ Added |
| HubSpot | API Key, Access Token, Client Secret | ✅ Added |

---

## Phase 1: Project Setup

### 1.1 Directory Structure
```
CRM_integration/
├── .env                 # API credentials (DO NOT COMMIT)
├── .env.example         # Template for credentials
├── .gitignore           # Ignore sensitive files
├── requirements.txt     # Python dependencies
├── SETUP_PLAN.md        # This file
├── data/
│   └── sales_tracking.xlsx  # Master subscriber list
├── src/
│   ├── __init__.py
│   ├── kajabi_client.py     # Kajabi API wrapper
│   ├── hubspot_client.py    # HubSpot API wrapper
│   ├── excel_sync.py        # Excel read/write operations
│   └── sync_pipeline.py     # Main orchestration
└── logs/
    └── sync.log             # Sync operation logs
```

### 1.2 Dependencies
```
python-dotenv        # Load .env files
requests             # HTTP requests
hubspot-api-client   # Official HubSpot SDK
openpyxl             # Excel file handling
pandas               # Data manipulation
```

**Status:** ⬜ Not Started

---

## Phase 2: HubSpot Setup

### 2.1 Custom Contact Properties to Create

| Property Name | Internal Name | Type | Description |
|--------------|---------------|------|-------------|
| Credentials | credentials | Single-line text | MD, DO, DC, etc. |
| Organization | organization | Single-line text | Practice/Company name |
| Specialty | specialty | Single-line text | Orthopaedic, Internal Medicine, etc. |
| Year Acquired | year_acquired | Number | Year became customer |
| Courses Ordered | courses_ordered | Multi-line text | List of courses purchased |
| Subscriber Number | subscriber_number | Number | Legacy subscriber # |

### 2.2 Contact List/Pipeline
- Create "TeachCE Subscribers" contact list
- Optional: Pipeline for tracking course completion

**Status:** ⬜ Not Started

---

## Phase 3: Kajabi Integration

### 3.1 API Endpoints Needed
- `GET /orders` - Fetch all orders
- `GET /offers` - Get course/offer details
- `GET /contacts` - Get customer info

### 3.2 Authentication
Kajabi uses OAuth2:
1. Use client_id and client_secret
2. Get access token
3. Include token in API requests

### 3.3 Data Mapping (Kajabi → Master List)

| Kajabi Field | Excel Column |
|--------------|--------------|
| Name | Name + Last Name |
| Email | Email |
| Billing Street | Street Address |
| Billing City | City |
| Billing Province | St |
| Billing Zip | Zip |
| Phone | Phone |
| Lineitem name | Courses Ordered (append) |
| Created at | Year Acquired (extract year) |
| Total | Payment |

**Status:** ⬜ Not Started

---

## Phase 4: Excel Sync Module

### 4.1 Logic
1. Load existing `sales_tracking.xlsx`
2. For each new Kajabi order:
   - Check if customer exists (match by Email)
   - If exists: Append course to "Courses Ordered"
   - If new: Add new row with all fields
3. Save updated spreadsheet

### 4.2 Master Spreadsheet Columns
From existing file:
- #Subscribers, Name, Last Name, Credentials, Organization
- Street Address, City, St, Zip
- Specialty, Year Acquired, Start, Payment
- Phone, Fax, Email, Email 2
- Courses Ordered

**Status:** ⬜ Not Started

---

## Phase 5: HubSpot Sync

### 5.1 Logic
1. For each customer in Excel:
   - Search HubSpot for existing contact (by email)
   - If exists: Update properties
   - If new: Create contact
2. Map Excel columns to HubSpot properties

### 5.2 HubSpot API Operations
- `POST /crm/v3/objects/contacts` - Create contact
- `PATCH /crm/v3/objects/contacts/{id}` - Update contact
- `GET /crm/v3/objects/contacts/search` - Find by email

**Status:** ⬜ Not Started

---

## Phase 6: Main Pipeline

### 6.1 Sync Script Flow
```python
def run_sync():
    # 1. Fetch new orders from Kajabi (since last sync)
    new_orders = kajabi_client.get_orders(since=last_sync_date)

    # 2. Update Excel spreadsheet
    excel_sync.update_spreadsheet(new_orders)

    # 3. Sync all contacts to HubSpot
    hubspot_client.sync_contacts(excel_data)

    # 4. Log results
    log_sync_results()
```

### 6.2 Scheduling Options
- Manual: Run script when needed
- Cron job: Daily/weekly automatic sync
- Webhook: Trigger on new Kajabi sale (if supported)

**Status:** ⬜ Not Started

---

## Phase 7: Testing & Validation

### 7.1 Test Cases
- [ ] New customer purchase → Added to Excel + HubSpot
- [ ] Existing customer buys another course → Course appended
- [ ] Duplicate detection working
- [ ] All fields mapping correctly

### 7.2 Validation
- Compare Excel row count before/after
- Verify HubSpot contact properties match Excel
- Check for data integrity issues

**Status:** ⬜ Not Started

---

## Progress Tracker

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Project Setup | ✅ Complete |
| 2 | HubSpot Setup | ✅ Complete |
| 3 | Kajabi Integration | ✅ Complete & Tested |
| 4 | Excel Sync Module | ✅ Complete & Tested |
| 5 | HubSpot Sync | ✅ Complete & Tested |
| 6 | Main Pipeline | ✅ Complete & Tested |
| 7 | Testing & Validation | ✅ Complete |

---

## Bug Fixes Applied (2026-01-15)

### 1. HubSpot SDK Compatibility
**File:** `src/hubspot_client.py:187-190`
- Changed `SimplePublicObjectInput` to `SimplePublicObjectInputForCreate` for creating contacts
- Updated parameter name from `simple_public_object_input` to `simple_public_object_input_for_create`

### 2. NaN Value Handling
**File:** `src/hubspot_client.py:15-21, 195, 221`
- Added `is_nan()` helper function to detect None and float NaN values
- Filters out NaN values from all API requests (both create and update)

### 3. Email Whitespace
**File:** `src/sync_pipeline.py:163`
- Added `.strip()` to clean trailing spaces from email addresses
- Fixed "invalid email" errors from HubSpot API

### 4. Field Name Mapping
**File:** `src/sync_pipeline.py:143-144`
- Changed `first_name`/`last_name` to `firstname`/`lastname` for HubSpot compatibility

### 5. Kajabi API URL Fix (2026-01-15)
**File:** `src/kajabi_client.py:18, 39`
- Changed `BASE_URL` from `https://kajabi.com/api/v1` to `https://api.kajabi.com/v1`
- Changed auth URL from `https://kajabi.com/oauth/token` to `https://api.kajabi.com/v1/oauth/token`

### 6. Kajabi JSON:API Format
**File:** `src/kajabi_client.py:64-161`
- Updated `get_orders()` to use `/purchases` endpoint with `data` key
- Added `_normalize_purchase()`, `_normalize_offer()`, `_normalize_contact()` helpers
- Properly handles JSON:API response format

---

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| HubSpot Properties | ✅ Working | 6 custom properties created |
| Excel Sync | ✅ Working | 1,770 subscribers loaded |
| HubSpot Contacts | ✅ Working | Create/update contacts |
| Kajabi Auth | ✅ Working | OAuth2 client_credentials |
| Kajabi Purchases | ✅ Working | 30 purchases available |
| Kajabi Contacts | ✅ Working | 25 contacts available |
| Kajabi Offers | ✅ Working | 30 offers/courses |

---

## Files Reference

| File | Purpose |
|------|---------|
| `.env` | API credentials |
| `data/sales_tracking.xlsx` | Master subscriber list (copied from Downloads) |
| `/mnt/c/Users/Gregory/OneDrive/Desktop/Kajabi/*.csv` | Historical Kajabi order exports |

---

## Notes

- Original subscriber list: `/mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/data/sales_tracking.xlsx`
- Kajabi order exports: `/mnt/c/Users/Gregory/OneDrive/Desktop/Kajabi/`
- HubSpot Portal ID still needed (can get from HubSpot dashboard)

---

---

## Automation Setup

### Manual Run
```bash
cd /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration
./sync.sh              # Full sync
./sync.sh kajabi       # Kajabi → Excel only
./sync.sh hubspot      # Excel → HubSpot only
```

### Cron (WSL/Linux)
```bash
# Open crontab editor
crontab -e

# Add this line for daily sync at 6:00 AM:
0 6 * * * /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/sync.sh full

# Other schedules:
# Every hour: 0 * * * * /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/sync.sh full
# Twice daily (6 AM and 6 PM): 0 6,18 * * * /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/sync.sh full
# Every Monday at 9 AM: 0 9 * * 1 /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/sync.sh full

# Verify cron is running
sudo service cron status

# Start cron if needed
sudo service cron start
```

### Logs
Sync logs are saved to: `logs/sync_YYYYMMDD_HHMMSS.log`

---

*Last Updated: 2026-01-15*
