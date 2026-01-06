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

- `KAJABI_API_KEY`: Your Kajabi API key
- `KAJABI_API_SECRET`: Your Kajabi API secret
- `HUBSPOT_ACCESS_TOKEN`: Your HubSpot personal access token
- `POLL_INTERVAL`: (Optional) Minutes between checks when using scheduler (default: 5)

## File Structure

```
agent/
├── index.js           # Main integration script
├── scheduler.js       # Runs integration on a schedule
├── config.js          # Configuration management
├── package.json       # Dependencies
├── .env              # API credentials (DO NOT COMMIT)
├── .gitignore        # Protects sensitive files
└── sales_data.xlsx   # Generated Excel file with sales data
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

## Current Status (January 5, 2026)

- ✓ Kajabi API integration working with OAuth2
- ✓ HubSpot API integration working with Personal Access Token
- ✓ Excel export functional
- ⚠ Duplicate contact handling needs improvement (currently in progress)
- Planned: Date-based filtering for new purchases only

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

## License

MIT
