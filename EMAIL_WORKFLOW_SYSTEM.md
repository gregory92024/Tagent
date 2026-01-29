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

## 7. TASK INSTRUCTIONS FOR CLAUDE

### Task: Generate Renewal List
```
1. Open the Excel file at the source path
2. Filter for Payment dates older than 11 months from today
3. Exclude any records matching exclusion rules
4. Return list with: Name, Email, Last Payment Date, Credits, Specialty
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
1. Count total active subscribers (Payment date within 12 months)
2. Count subscribers due for renewal (11-12 months)
3. Count inactive subscribers (18+ months)
4. List any pending certificate holds
```

---

## 8. SCALING NOTES

This system is designed to scale. As new subscribers are added:
- They will follow the same column structure
- New staff initials can be added to Section 2
- Workflow triggers apply automatically based on dates
- No structural changes needed for growth

---

## 9. VERSION HISTORY

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-11 | 1.0 | Initial system documentation created |

---

## 10. QUICK REFERENCE

**Source File**: `/mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/data/sales_tracking.xlsx`
**Email Platform**: Outlook
**Active Staff**: GH, DH, TS
**Primary Email Column**: P (Email)
**Last Activity Column**: R (Courses Ordered)
**Payment Date Column**: M (Payment)
