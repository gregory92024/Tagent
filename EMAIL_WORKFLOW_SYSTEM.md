# Email Workflow System - Source of Truth

> **Purpose**: This document defines the data source, rules, and workflows for client email management. Claude Code should reference this document when executing any email-related tasks.

---

## 1. DATA SOURCE

### Primary Source File
```
Path: /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/data/sales_tracking.xlsx
Type: Microsoft Excel Workbook
Status: ACTIVE - Source of Truth
```

### Data Structure

| Column | Field Name | Type | Description |
|--------|-----------|------|-------------|
| A | # | Number | Subscriber ID |
| B | Subscribers Name | Text | First name |
| C | Last Name | Text | Last name |
| D | Credentials | Text | Professional credentials (MD, DC, PhD, DO, DPM, etc.) |
| E | Organization | Text | Practice/employer name |
| F | Street Address | Text | Mailing address |
| G | City | Text | City |
| H | St | Text | State abbreviation |
| I | Zip | Number | Zip code |
| J | Specialty | Text | Medical specialty |
| K | Year Acquired | Number | Year subscriber was acquired |
| L | Start | Text | Credits purchased (e.g., "12 credits 9-08") |
| M | Payment | Date | Payment/order date |
| N | Phone | Text | Phone number |
| O | Fax | Text | Fax number |
| P | Email | Text | Primary email address |
| Q | Email 2 | Text | Secondary email (optional) |
| R | Courses Ordered | Text | Detailed notes on courses, dates, delivery method |

### Special Flags in Data
- `"COMPETITOR - DON'T SEND MARKETING INFO"` - Do NOT send any marketing emails
- `"Do not issue certificate until after [Month] exam"` - Certificate hold pending exam results
- `"no classes logged"` - No course activity recorded
- `"self"` - Self-employed/individual subscriber

---

## 2. STAFF TRACKING

### Legacy Staff (Historical Reference Only)
| Initials | Status |
|----------|--------|
| SG | Legacy |
| DL | Legacy |

### Active Staff
| Initials | Status |
|----------|--------|
| GH | Active |
| DH | Active |
| TS | Active |

### Note Format for Courses Ordered
When logging new activity, use this format:
```
[INITIALS] [action] [course numbers] ([credits] credits) on [M/D/YY]
```
Examples:
- `GH emailed 201, 206, 218 & 224 (6 credits) on 1/11/26`
- `TS mailed 200, 202, 212 (12 credits) via Priority Mail on 1/11/26`
- `Online order 202, 204 (6 credits) on 1.11.26`

---

## 3. EMAIL PLATFORM

**Platform**: Microsoft Outlook
**Integration**: Browser automation via Claude in Chrome or direct Outlook integration

---

## 4. WORKFLOW TRIGGERS

### Time-Based Triggers

| Trigger Name | Condition | Action |
|-------------|-----------|--------|
| Annual Renewal | 11 months since last Payment date | Send renewal reminder |
| Re-engagement | 18+ months since last Payment date | Send re-engagement email |
| Follow-up | 7 days after course materials sent | Send follow-up/check-in |
| Expiring Credits | 30 days before credit expiration (if applicable) | Send expiration warning |

### Status-Based Triggers

| Trigger Name | Condition | Action |
|-------------|-----------|--------|
| Certificate Hold | "Do not issue certificate until" in notes | Track and follow up after exam date |
| No Activity | "no classes logged" in Courses Ordered | Flag for outreach campaign |
| Incomplete Order | Partial credits in recent order | Suggest additional courses |
| New Subscriber | Year Acquired = current year, no courses | Send welcome sequence |

---

## 5. EMAIL TEMPLATES (To Be Defined)

### Template Categories
1. **Renewal Reminders** - Annual credit renewal notifications
2. **Follow-ups** - Post-order check-ins
3. **Re-engagement** - Win-back inactive subscribers
4. **Pre-emptive** - Proactive outreach before expiration
5. **Welcome** - New subscriber onboarding
6. **Certificate Ready** - Notification when certificate is available

> **Note**: Actual email templates will be added as they are created.

---

## 6. EXCLUSION RULES

**Do NOT send emails to subscribers who:**
1. Have "COMPETITOR" anywhere in their record
2. Have "DON'T SEND MARKETING" in their record
3. Have no valid email address
4. Have explicitly opted out (to be tracked separately)

---

## 7. CLI COMMANDS

The email workflow is implemented in `src/email_workflow.py` and `src/email_tracking.py` with CLI access via `run.py`:

```bash
# Show renewal status summary (counts only)
python run.py --renewal-status

# Show all renewal candidates with details
python run.py --renewal-list

# Daily check: conversions + due reminders (run this daily)
python run.py --renewal-check

# Preview emails ready to send with personalized content
python run.py --renewal-send

# Mark email as sent for subscriber (after manually sending)
python run.py --mark-sent 1525.0

# Mark response received from subscriber
python run.py --mark-response 1362.0
```

### Renewal Window Configuration
- **Renewal Cycle**: 24 months (2 years)
- **Reminder Window**: 18-24 months after payment (6 months before renewal)
- **Exclusions**: No email, COMPETITOR flag, DON'T SEND MARKETING flag

### Escalating Reminder Schedule
| Reminder | Timing | Months After Payment |
|----------|--------|---------------------|
| 1st | 6 months before renewal | 18 months |
| 2nd | 3 months before renewal | 21 months |
| 3rd | 1 month before renewal | 23 months |

**Logic**: Only send next reminder if:
- Previous reminder was sent
- No response recorded
- No conversion (new payment) detected

### Sample Output (--renewal-status)
```
============================================================
RENEWAL REMINDER REPORT
============================================================
Generated: 2026-01-30 00:53

Renewal Window: Payment between 2024-01-30 and 2024-07-30
(18-24 months since payment)

----------------------------------------
STATUS SUMMARY
----------------------------------------
Total records:             1770
Renewal candidates:         189
Lapsed (>24 months):       1224
Current (<18 months):       112
No payment date:             26

----------------------------------------
EXCLUSIONS
----------------------------------------
No email address:           219
Competitor:                   0
Marketing opt-out:            0
```

---

## 7A. EMAIL TRACKING SYSTEM

### Storage File
```
Path: /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/data/email_tracking.json
```

### Data Structure
```json
{
  "contacts": {
    "subscriber_123": {
      "email": "user@example.com",
      "payment_date": "2024-02-08",
      "reminder_1_sent": "2026-01-30",
      "reminder_2_sent": null,
      "reminder_3_sent": null,
      "status": "pending",
      "response_date": null,
      "conversion_date": null
    }
  },
  "last_check": "2026-01-30T06:00:00"
}
```

### Contact Status Values
| Status | Description |
|--------|-------------|
| `pending` | Active in reminder queue |
| `responded` | Contact replied to email |
| `converted` | Made a new purchase |
| `lapsed` | Did not renew after all reminders |

### Email Template
Located at: `templates/renewal_reminder.txt`

**Available placeholders:**
- `{first_name}` - Contact first name
- `{last_name}` - Contact last name
- `{email}` - Email address
- `{subscriber_id}` - Subscriber ID
- `{payment_date}` - Last payment date (formatted)
- `{courses_ordered}` - Courses from last order
- `{renewal_deadline}` - Calculated renewal deadline

### Daily Cron Job
```bash
# Setup cron job (runs daily at 6:00 AM)
./setup_renewal_cron.sh

# Manual test
./renewal_cron.sh

# View logs
cat logs/renewal_cron.log
```

### Data Flow
```
                    Daily Cron Job
                          │
                          ▼
┌─────────────────────────────────────────────────┐
│  1. Load email_tracking.json                    │
│  2. Check Kajabi for new purchases              │
│  3. Mark conversions in tracking                │
│  4. Calculate who needs reminder (18/21/23 mo)  │
│  5. Cross-reference with tracking (sent status) │
│  6. Generate "due for email" list               │
│  7. Save tracking state                         │
└─────────────────────────────────────────────────┘
                          │
                          ▼
            Console Report / Log File
                          │
                          ▼
         Manual: Review + Send via Outlook
                          │
                          ▼
         python run.py --mark-sent {ID}
```

---

## 8. TASK INSTRUCTIONS FOR CLAUDE

### Task: Generate Renewal List
```
1. Run: python run.py --renewal-list
2. Or use EmailWorkflow class directly:
   from src.email_workflow import EmailWorkflow
   workflow = EmailWorkflow()
   candidates = workflow.get_renewal_candidates()
```

### Task: Log New Activity
```
1. Open the Excel file
2. Find subscriber by name or ID
3. Append to "Courses Ordered" column using note format
4. Save the workbook
```

### Task: Send Email via Outlook
```
1. Confirm recipient is not in exclusion list
2. Use appropriate template for email type
3. Personalize with subscriber data
4. Request user confirmation before sending
5. Log the action in Courses Ordered column
```

### Task: Weekly Status Report
```
1. Run: python run.py --renewal-status
2. Review counts for renewal candidates and exclusions
3. Check for any pending certificate holds manually
```

---

## 9. SCALING NOTES

This system is designed to scale. As new subscribers are added:
- They will follow the same column structure
- New staff initials can be added to Section 2
- Workflow triggers apply automatically based on dates
- No structural changes needed for growth

---

## 10. VERSION HISTORY

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-30 | 1.2 | Phase 2: Added email tracking system, escalating reminders, conversion detection, new CLI commands (`--renewal-check`, `--renewal-send`, `--mark-sent`, `--mark-response`), cron automation |
| 2026-01-30 | 1.1 | Added CLI commands (`--renewal-status`, `--renewal-list`), implemented `src/email_workflow.py` |
| 2026-01-11 | 1.0 | Initial system documentation created |

---

## 11. QUICK REFERENCE

**Source File**: `/mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/data/sales_tracking.xlsx`
**Tracking File**: `/mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/data/email_tracking.json`
**Email Template**: `/mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/templates/renewal_reminder.txt`
**Email Platform**: Outlook (manual send, response tracking via CLI)
**Active Staff**: GH, DH, TS
**Primary Email Column**: P (Email)
**Last Activity Column**: R (Courses Ordered)
**Payment Date Column**: M (Payment)
**Daily Cron**: `./renewal_cron.sh` (runs at 6:00 AM)
**Cron Log**: `logs/renewal_cron.log`
