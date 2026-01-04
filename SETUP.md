# Setup Guide

Complete setup instructions for the Kajabi → HubSpot → Excel Integration

## Prerequisites

- Node.js (v14 or higher)
- npm (comes with Node.js)
- Kajabi account with API access
- HubSpot account with admin/developer access

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd /mnt/c/Users/Gregory/OneDrive/Desktop/agent
npm install
```

This will install:
- `axios` - HTTP client for API calls
- `@hubspot/api-client` - Official HubSpot SDK
- `exceljs` - Excel file generation
- `dotenv` - Environment variable management

### 2. API Credentials Configuration

All credentials are stored in the `.env` file:

#### Kajabi API
- **API Key:** Located in Kajabi Settings → Integrations → API
- **API Secret:** Provided with the API key

#### HubSpot API
- **Personal Access Token:**
  1. Go to HubSpot Settings
  2. Navigate to Integrations → Private Apps
  3. Create or access your personal access key
  4. Copy the token

**Example Configuration:**
```
KAJABI_API_KEY=your_kajabi_api_key_here
KAJABI_API_SECRET=your_kajabi_api_secret_here
HUBSPOT_ACCESS_TOKEN=your_hubspot_access_token_here
```

### 3. HubSpot Permissions

Ensure your HubSpot access token has these permissions:
- `crm.objects.contacts.read`
- `crm.objects.contacts.write`
- `crm.objects.deals.read`
- `crm.objects.deals.write`

### 4. Test the Connection

Run a single sync to test:
```bash
npm start
```

Expected output:
```
Starting Kajabi → HubSpot → Excel integration...
Fetching sales from Kajabi...
Found X sales from Kajabi
Processing sale: [sale_id]
Created HubSpot contact: [email]
Created HubSpot deal for [product]
Excel file updated: /path/to/sales_data.xlsx
✓ Integration completed successfully!
```

### 5. Run Continuously

Start the scheduler for automatic syncing every 5 minutes:
```bash
npm run schedule
```

To stop: Press `Ctrl+C`

## Troubleshooting

### Authentication Errors
- Verify API keys in `.env` file
- Check HubSpot token hasn't expired
- Ensure Kajabi API access is enabled

### No Sales Found
- Check Kajabi account has recent purchases
- Verify API endpoint is correct
- Check API rate limits

### Excel File Issues
- Ensure write permissions in the directory
- Check disk space availability
- Verify ExcelJS is installed correctly

### HubSpot Errors
- Verify contact email format is valid
- Check deal pipeline exists
- Ensure proper permissions are set

## File Locations

- **Project:** `/mnt/c/Users/Gregory/OneDrive/Desktop/agent`
- **Excel Output:** `/mnt/c/Users/Gregory/OneDrive/Desktop/agent/sales_data.xlsx`
- **Logs:** Console output (can be redirected to file)

## Security Notes

- Never commit `.env` file to version control
- Keep API keys secure and private
- Rotate keys periodically
- Use environment-specific credentials for testing vs production
