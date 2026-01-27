# Sales Automation Integration

This project automates the flow of sales data from Kajabi to HubSpot CRM and Excel.

## Components

- **Kajabi Integration**: Monitors and retrieves new sales
- **HubSpot CRM**: Creates/updates contacts and deals automatically
- **Excel Export**: Maintains a spreadsheet of all sales data

## Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment variables**
   All API keys are already set in `.env` file

3. **Run the integration**
   ```bash
   # Run once
   npm start

   # Run on a schedule (checks every 5 minutes)
   npm run schedule

   # Development mode with auto-reload
   npm run dev
   ```

## How It Works

1. **Fetches sales** from Kajabi API
2. **Creates/updates contacts** in HubSpot CRM
3. **Creates deals** in HubSpot linked to contacts
4. **Updates Excel file** (`sales_data.xlsx`) with all sales records

## Environment Variables

- `KAJABI_API_KEY`: Your Kajabi API key (OAuth2 client ID)
- `KAJABI_API_SECRET`: Your Kajabi API secret (OAuth2 client secret)
- `HUBSPOT_ACCESS_TOKEN`: Your HubSpot personal access token (PAT)
- `POLL_INTERVAL`: (Optional) Minutes between checks when using scheduler (default: 5)
- `PURCHASE_CUTOFF_DATE`: (Optional) ISO 8601 date - only process purchases created after this date (default: 2026-01-05T08:00:00Z)

## File Structure

```
Agent/
├── index.js              # Main integration script
├── scheduler.js          # Scheduled runner
├── config.js             # Configuration loader
├── package.json          # Dependencies & scripts
├── .env                  # Credentials (gitignored)
├── .env.example          # Template for credentials
├── sync_state.json       # Auto-advancing cutoff (gitignored)
├── sales_data.xlsx       # Generated output (gitignored)
├── README.md             # This file
├── SETUP.md              # Setup instructions
├── USAGE.md              # Usage guide
├── API_DOCUMENTATION.md  # Technical reference
├── CHANGELOG.md          # Version history
└── STATUS.md             # Current status
```

## Sync State Tracking

The integration maintains a `sync_state.json` file to track progress:

```json
{
  "last_sync": "2026-01-27T11:32:33.033Z",
  "last_purchase_date": "2026-01-27T04:35:29.191Z",
  "cutoff_for_next_run": "2026-01-27T04:35:29.191Z"
}
```

**How it works:**
- On first run, uses `PURCHASE_CUTOFF_DATE` from `.env`
- After processing, saves the latest purchase date
- Next run automatically uses saved cutoff (no manual updates needed)
- Prevents re-processing old purchases on subsequent runs

**To reset and re-sync all purchases:**
```bash
rm sync_state.json
npm start
```

## Usage

**One-time sync:**
```bash
npm start
```

**Continuous monitoring:**
```bash
npm run schedule
```

The scheduler will automatically check for new sales every 5 minutes and sync them to HubSpot and Excel.

## Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions and troubleshooting
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference and technical details
- **[USAGE.md](USAGE.md)** - Common use cases and examples

## Features

✓ Automated sales synchronization from Kajabi
✓ OAuth2 authentication for Kajabi API
✓ JSON:API format support with relationship mapping
✓ Smart contact management (creates new, updates existing)
✓ Deal creation with contact associations
✓ Excel export with formatted data
✓ Configurable polling interval
✓ Error handling and logging
✓ Secure credential management

## Current Status (January 27, 2026)

- ✓ Kajabi API integration working with OAuth2
- ✓ HubSpot API integration working with Personal Access Token
- ✓ Excel export functional with duplicate prevention
- ✓ Duplicate contact handling fixed - properly updates existing contacts
- ✓ Auto-advancing cutoff date via `sync_state.json`
- ✓ 303+ deals synced to HubSpot

## Requirements

- Node.js v14 or higher
- Active Kajabi account with API access
- HubSpot account with CRM access
- Valid API credentials configured in `.env`

## Quick Start

```bash
# Clone or navigate to project
cd /mnt/c/Users/Gregory/OneDrive/Desktop/agent

# Install dependencies
npm install

# Run once to test
npm start

# Run continuously
npm run schedule
```

## Support

For issues or questions:
1. Check [SETUP.md](SETUP.md) for troubleshooting
2. Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
3. Check console logs for error messages

## Security

- API credentials stored in `.env` (not committed to git)
- Follows security best practices
- Regular credential rotation recommended

## Related Projects

- **[CRM_integration](../CRM_integration/)** - Python project for enriching HubSpot contacts with extended data
- **[SYNC_RUN_ORDER.md](../SYNC_RUN_ORDER.md)** - Run order and scheduling between projects

## License

MIT
