# Email Automation Setup Guide

> **Purpose**: Step-by-step configuration checklist to fully set up the email workflow system. Complete each section before going live.

---

## SETUP STATUS

| Phase | Status | Completed By | Date |
|-------|--------|--------------|------|
| 1. Data Source | COMPLETE | TS | 2026-01-11 |
| 2. Staff Configuration | COMPLETE | TS | 2026-01-11 |
| 3. Email Platform | PENDING | - | - |
| 4. Template Creation | PENDING | - | - |
| 5. Trigger Rules | PENDING | - | - |
| 6. Exclusion Lists | PENDING | - | - |
| 7. Testing | PENDING | - | - |
| 8. Go Live | PENDING | - | - |

---

## PHASE 1: DATA SOURCE CONFIGURATION ✅

### Questions Answered
- [x] Where is the source file located?
  - **Answer**: `/mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/data/sales_tracking.xlsx`

- [x] What columns contain critical data?
  - **Answer**: See EMAIL_WORKFLOW_SYSTEM.md Section 1

- [x] Will the file location change?
  - **Answer**: TBD - Consider moving to a stable location

### Outstanding Questions
- [ ] Should we move the Excel file to ~/Teach or another permanent location?
- [ ] Will there be a backup/versioning system for the Excel file?
- [ ] How often will new subscribers be added (daily, weekly, monthly)?

---

## PHASE 2: STAFF CONFIGURATION ✅

### Questions Answered
- [x] Who are the legacy staff members?
  - **Answer**: SG, DL (historical reference only)

- [x] Who are the active staff members?
  - **Answer**: GH, DH, TS

### Outstanding Questions
- [ ] Should each staff member have specific responsibilities? (e.g., GH handles renewals, DH handles new subscribers)
- [ ] Do staff members need individual Outlook accounts or one shared account?
- [ ] Who approves emails before sending? (One person or any staff?)

---

## PHASE 3: EMAIL PLATFORM SETUP ⏳

### Questions to Answer

#### Outlook Configuration
- [ ] **Account Type**: Personal Outlook, Microsoft 365 Business, or shared mailbox?
  - Options: Personal | Business | Shared Mailbox
  - Answer: _________________

- [ ] **Sending Address**: What email address will emails come FROM?
  - Answer: _________________

- [ ] **Reply-To Address**: Where should replies go?
  - Options: Same as sending | Different address | No-reply
  - Answer: _________________

- [ ] **Signature**: What signature should appear on emails?
  - Answer: _________________

#### Automation Method
- [ ] **How should Claude send emails?**
  - Options:
    - Browser automation (Claude in Chrome controls Outlook Web)
    - Manual review (Claude drafts, human sends)
    - API integration (if Microsoft 365)
  - Answer: _________________

- [ ] **Batch or Individual**: Send emails one-by-one or in batches?
  - Options: Individual (safer) | Batch (faster)
  - Answer: _________________

- [ ] **Daily Send Limit**: Maximum emails per day?
  - Recommended: Start with 20-50/day to avoid spam flags
  - Answer: _________________

---

## PHASE 4: EMAIL TEMPLATES ⏳

### Templates Needed

#### Template 1: Renewal Reminder
- [ ] Subject line: _________________
- [ ] Body copy: _________________
- [ ] Call to action: _________________
- [ ] Personalization fields: Name, Credits, Last Order Date
- [ ] Send timing: ___ days before renewal due

#### Template 2: Follow-Up (Post-Order)
- [ ] Subject line: _________________
- [ ] Body copy: _________________
- [ ] Call to action: _________________
- [ ] Personalization fields: Name, Courses Ordered
- [ ] Send timing: ___ days after order

#### Template 3: Re-Engagement (Inactive)
- [ ] Subject line: _________________
- [ ] Body copy: _________________
- [ ] Call to action: _________________
- [ ] Personalization fields: Name, Last Activity Date
- [ ] Send timing: After ___ months of inactivity

#### Template 4: Pre-Emptive Outreach
- [ ] Subject line: _________________
- [ ] Body copy: _________________
- [ ] Call to action: _________________
- [ ] Personalization fields: _________________
- [ ] Send timing: _________________

#### Template 5: Welcome (New Subscriber)
- [ ] Subject line: _________________
- [ ] Body copy: _________________
- [ ] Call to action: _________________
- [ ] Personalization fields: Name, Specialty
- [ ] Send timing: Immediately after sign-up

#### Template 6: Certificate Ready
- [ ] Subject line: _________________
- [ ] Body copy: _________________
- [ ] Call to action: _________________
- [ ] Personalization fields: Name, Course, Certificate details
- [ ] Send timing: When certificate is issued

### Template Questions
- [ ] Should templates include images/logos?
- [ ] Plain text or HTML formatted?
- [ ] Include unsubscribe link? (Required by law for marketing)
- [ ] Track email opens/clicks?

---

## PHASE 5: TRIGGER RULES ⏳

### Time-Based Triggers

| Trigger | Current Setting | Confirm/Change |
|---------|----------------|----------------|
| Renewal Reminder | 11 months since last payment | [ ] Confirm / Change to: ___ |
| Re-engagement | 18+ months inactive | [ ] Confirm / Change to: ___ |
| Follow-up | 7 days after order | [ ] Confirm / Change to: ___ |
| Credit Expiration Warning | 30 days before | [ ] Confirm / Change to: ___ |

### Status-Based Triggers

| Trigger | Current Setting | Confirm/Change |
|---------|----------------|----------------|
| Certificate Hold | Track "Do not issue" notes | [ ] Confirm / Disable |
| No Activity | Flag "no classes logged" | [ ] Confirm / Disable |
| Incomplete Order | Partial credits | [ ] Confirm / Disable |
| New Subscriber | Year Acquired = current, no courses | [ ] Confirm / Disable |

### Trigger Questions
- [ ] Should triggers run automatically or require manual approval each time?
- [ ] What time of day should emails send? (Morning recommended: 9-10 AM)
- [ ] Which days of week? (Tue-Thu typically best open rates)
- [ ] How to handle multiple triggers for same person? (Priority order)

---

## PHASE 6: EXCLUSION LISTS ⏳

### Current Exclusions
- [x] Records containing "COMPETITOR"
- [x] Records containing "DON'T SEND MARKETING"
- [x] Records with no valid email

### Additional Exclusion Questions
- [ ] Create a separate opt-out tracking list?
  - Options: Add column to Excel | Separate file | Both
  - Answer: _________________

- [ ] How should opt-outs be processed?
  - Options: Manual removal | Automated flagging
  - Answer: _________________

- [ ] Any specialties to exclude from certain campaigns?
  - Answer: _________________

- [ ] Exclude recently contacted? (e.g., no email if contacted in last 30 days)
  - Answer: _________________

---

## PHASE 7: TESTING ⏳

### Pre-Launch Checklist

#### Data Validation
- [ ] Run test query to verify data reads correctly
- [ ] Confirm date parsing works (Payment column)
- [ ] Verify exclusion rules filter correctly
- [ ] Test with known subscriber record

#### Email Testing
- [ ] Send test email to staff member
- [ ] Verify personalization fields populate
- [ ] Check formatting on desktop and mobile
- [ ] Confirm reply-to address works
- [ ] Test unsubscribe process (if applicable)

#### Workflow Testing
- [ ] Run renewal trigger on small batch (5 people)
- [ ] Verify logging works (Courses Ordered updates)
- [ ] Confirm no duplicates sent
- [ ] Test manual override/cancel

### Test Contacts
| Name | Email | Purpose |
|------|-------|---------|
| | | Test recipient 1 |
| | | Test recipient 2 |
| | | Test recipient 3 |

---

## PHASE 8: GO LIVE ⏳

### Launch Checklist
- [ ] All phases above marked complete
- [ ] Staff trained on system
- [ ] Backup of Excel file created
- [ ] Emergency stop procedure documented
- [ ] First batch size decided: ___ emails
- [ ] Go-live date: ___________

### Emergency Procedures
- **To stop all emails**: [Document procedure]
- **To undo a mistake**: [Document procedure]
- **Contact for issues**: [Document contact]

---

## QUICK COMMANDS FOR CLAUDE

Once setup is complete, use these commands:

```
"Show me everyone due for renewal"
"Draft renewal emails for this week"
"Log that GH sent courses 201, 206 to [Name]"
"Generate weekly status report"
"Who hasn't ordered in 18+ months?"
"Check for certificate holds"
```

---

## NOTES & DECISIONS LOG

| Date | Decision | Made By |
|------|----------|---------|
| 2026-01-11 | Created system documentation | TS |
| 2026-01-11 | Set active staff as GH, DH, TS | TS |
| | | |
| | | |

---

## FILES REFERENCE

| File | Location | Purpose |
|------|----------|---------|
| Source Data | `/mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/data/sales_tracking.xlsx` | Master subscriber list |
| System Docs | `/mnt/c/Users/Gregory/OneDrive/Desktop/EMAIL_WORKFLOW_SYSTEM.md` | Rules and definitions |
| Setup Guide | `/mnt/c/Users/Gregory/OneDrive/Desktop/EMAIL_AUTOMATION_SETUP.md` | This file - configuration checklist |
