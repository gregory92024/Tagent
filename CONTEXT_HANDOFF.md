# Context Handoff - CRM Integration Discussion
**Created:** 2026-01-16
**Branch:** tim-dev (safe dev branch, main is protected)

---

## CURRENT DISCUSSION - RESUME HERE

We are discussing whether to add **HubSpot Deal creation** to the pipeline. The user noticed:

1. Deals exist in HubSpot with "No Owner" in the Deal Owner field
2. User thought customer name should be there (but Deal Owner = HubSpot user, not customer)
3. Customer info IS visible when clicking into deal details

**KEY DISCOVERY:** Our current pipeline does NOT create Deals. We only sync Contacts.
- The Deals in HubSpot are coming from somewhere else (likely Kajabi's native HubSpot integration or Zapier)

**USER'S QUESTION:** Should we add purchase/deal syncing from Kajabi to HubSpot?

---

## WHAT THE PIPELINE CURRENTLY DOES

```
Kajabi Contacts → Excel Spreadsheet → HubSpot CONTACTS
```

**What we sync:** Customer info (name, email, phone, address, courses ordered)
**What we DON'T sync:** Purchases as Deals

---

## KAJABI DATA AVAILABLE

### Purchases (Sales) - We CAN fetch but DON'T use for Deals yet
```json
{
  "id": "2184507302",
  "amount": 45.0,
  "currency": "USD",
  "created_at": "2023-12-15T23:25:00.748Z",
  "payment_type": "single",
  "customer_id": "2207751125",  // Just an ID, need to lookup customer
  "offer_id": "2149261862"      // Course ID, need to lookup offer name
}
```

### Contacts (Customers)
```json
{
  "id": "2688025664",
  "name": "George Martinez",
  "email": "georgemartinezdc@gmail.com",
  "phone": null,
  "billing_street": null,
  "created_at": "2026-01-14T23:22:27.899Z"
}
```

### Offers (Courses)
```json
{
  "id": "2149261862",
  "title": "206. Rating Principles and Philosophy of the AMA Guides, 5th edition",
  "price": 45.0
}
```

**CHALLENGE:** Purchases only have `customer_id`, not full customer details. To create a Deal linked to a Contact, we need to:
1. Fetch purchase
2. Look up customer by customer_id
3. Look up offer by offer_id (to get course name)
4. Create Deal in HubSpot linked to the Contact

---

## PROJECT STATUS - ALL WORKING

| Component | Status |
|-----------|--------|
| Kajabi Auth | ✅ OAuth2 working |
| Kajabi Purchases | ✅ 30 purchases available |
| Kajabi Contacts | ✅ 25 contacts available |
| Kajabi Offers | ✅ 30 courses available |
| Excel Sync | ✅ 1,770 subscribers |
| HubSpot Contacts | ✅ Working |
| HubSpot Deals | ❌ NOT implemented yet |
| Git Repo | ✅ github.com/timothysepulvado/CRM_integration |
| Automation | ✅ sync.sh + launchd plist ready |

---

## FILE LOCATIONS

```
/Users/timothysepulvado/Teach/CRM_integration/
├── src/
│   ├── kajabi_client.py    # Kajabi API (auth, purchases, contacts, offers)
│   ├── hubspot_client.py   # HubSpot API (contacts only, no deals yet)
│   ├── excel_sync.py       # Excel operations
│   └── sync_pipeline.py    # Main orchestration
├── run.py                  # CLI entry point
├── sync.sh                 # Automation wrapper
├── SETUP_PLAN.md           # Full documentation
└── .env                    # API credentials (not in git)
```

---

## NEXT STEPS TO DISCUSS

1. **Do we want to add Deal creation?**
   - Would sync Kajabi purchases → HubSpot Deals
   - Each Deal linked to Contact (customer)
   - Include: amount, course name, date

2. **Deal Owner question:**
   - Deal Owner = HubSpot USER (salesperson), not customer
   - Could set default owner (e.g., Tim's HubSpot user ID)
   - Or leave as "No Owner" if no salesperson assigned

3. **What's currently creating Deals?**
   - Not our code
   - Likely Kajabi's native HubSpot integration
   - May want to disable that if we take over

---

## GIT STATUS

- **main branch:** Production, working, protected
- **tim-dev branch:** Currently checked out, safe for changes
- **GitHub:** https://github.com/timothysepulvado/CRM_integration (private)

---

## CREDENTIALS (in .env, not in git)

- KAJABI_CLIENT_ID, KAJABI_CLIENT_SECRET
- HUBSPOT_ACCESS_TOKEN, HUBSPOT_API_KEY, HUBSPOT_CLIENT_SECRET

---

## TO CONTINUE

### Task 1: Create CLAUDE.md (do this first)
No rules/best practices file exists yet. Create `CLAUDE.md` with:
- Project overview (Kajabi → Excel → HubSpot sync)
- Code style guidelines
- Git workflow (main = production, tim-dev = development)
- API credential handling (never commit .env)
- File structure documentation
- Testing requirements

### Task 2: Discuss Deal Syncing
User wants to discuss adding Deal syncing. Key questions:
1. Should we create Deals from Kajabi purchases?
2. Who should be Deal Owner?
3. Should we disable whatever is currently creating Deals?

Start by: "I'll first create the CLAUDE.md with project rules, then we can continue discussing Deal creation."
