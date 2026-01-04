# Usage Guide

Common usage scenarios and examples for the Kajabi-HubSpot integration

## Basic Usage

### One-Time Sync

Perfect for testing or manual syncs:

```bash
cd /mnt/c/Users/Gregory/OneDrive/Desktop/agent
npm start
```

**When to use:**
- Testing the integration
- Manual sync after making changes
- One-off data migration

### Continuous Monitoring

Automatically checks for new sales every 5 minutes:

```bash
npm run schedule
```

**When to use:**
- Production environment
- Real-time sales tracking
- Automated workflow

**To stop:** Press `Ctrl+C`

### Development Mode

Auto-reloads on file changes:

```bash
npm run dev
```

**When to use:**
- Making code changes
- Testing modifications
- Debugging

## Customization

### Change Poll Interval

Edit `.env` file:
```env
POLL_INTERVAL=10  # Check every 10 minutes instead of 5
```

### Modify Excel Output

Edit `index.js` to customize columns:

```javascript
worksheet.columns = [
  { header: 'Date', key: 'date', width: 15 },
  { header: 'Customer Name', key: 'name', width: 25 },
  { header: 'Email', key: 'email', width: 30 },
  { header: 'Product', key: 'product', width: 30 },
  { header: 'Amount', key: 'amount', width: 12 },
  { header: 'Status', key: 'status', width: 12 },
  // Add custom columns here
];
```

### Filter Sales Data

Add filtering logic in `fetchKajabiSales()`:

```javascript
async function fetchKajabiSales() {
  const response = await axios.get(`${KAJABI_BASE_URL}/v1/purchases`, {
    headers: kajabiHeaders
  });

  const sales = response.data.purchases || [];

  // Filter for sales in the last 24 hours
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);
  return sales.filter(sale => new Date(sale.created_at) > yesterday);
}
```

## Common Scenarios

### Scenario 1: Initial Data Migration

Sync all historical sales data once:

```bash
npm start
```

This will fetch all available sales from Kajabi and populate HubSpot.

### Scenario 2: Real-Time Monitoring

Keep HubSpot constantly updated:

```bash
npm run schedule
```

Leave this running in the background. Consider using a process manager like `pm2`:

```bash
npm install -g pm2
pm2 start scheduler.js --name kajabi-sync
pm2 logs kajabi-sync
```

### Scenario 3: Daily Batch Processing

Use with cron or Task Scheduler to run once daily:

**Linux/Mac (crontab):**
```bash
0 9 * * * cd /path/to/agent && npm start
```

**Windows (Task Scheduler):**
Create a task to run:
```cmd
cd /mnt/c/Users/Gregory/OneDrive/Desktop/agent && npm start
```

### Scenario 4: Testing New Features

Use development mode while making changes:

```bash
npm run dev
```

Make changes to `index.js`, save, and it auto-restarts.

## Monitoring

### View Logs

All output goes to console. To save logs:

```bash
npm start > sync.log 2>&1
```

Or with scheduler:

```bash
npm run schedule > sync.log 2>&1
```

### Check Excel File

The file updates after each sync:

```bash
# View file location
ls -l /mnt/c/Users/Gregory/OneDrive/Desktop/agent/sales_data.xlsx

# Open in Excel
explorer.exe sales_data.xlsx
```

### Verify HubSpot Data

1. Log into HubSpot
2. Go to Contacts → Contacts
3. Search for synced email addresses
4. Check associated Deals

## Troubleshooting

### Integration Not Running

**Check Node.js:**
```bash
node --version  # Should be v14+
```

**Check dependencies:**
```bash
npm install
```

### No Sales Syncing

**Verify API connection:**
```bash
# Check Kajabi
curl -H "Authorization: Bearer YOUR_KEY" https://api.kajabi.com/v1/purchases

# Check HubSpot in browser
https://app.hubspot.com/
```

**Check credentials:**
```bash
cat .env  # Verify all keys are present
```

### Excel File Not Created

**Check permissions:**
```bash
ls -la /mnt/c/Users/Gregory/OneDrive/Desktop/agent/
```

**Create manually:**
```bash
touch sales_data.xlsx
chmod 666 sales_data.xlsx
```

### Duplicate Contacts in HubSpot

The script automatically handles duplicates by email. If you see duplicates:
- Different email addresses create separate contacts
- Check for typos in email fields
- Review HubSpot duplicate management settings

## Performance Tips

### Large Data Sets

For thousands of sales:

1. **Add rate limiting:**
```javascript
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

for (const sale of sales) {
  await processSale(sale);
  await delay(100); // 100ms between sales
}
```

2. **Batch processing:**
```javascript
const batchSize = 50;
for (let i = 0; i < sales.length; i += batchSize) {
  const batch = sales.slice(i, i + batchSize);
  await Promise.all(batch.map(processSale));
}
```

3. **Filter by date:**
Only sync recent sales instead of all historical data.

## Advanced Configuration

### Use with PM2 (Process Manager)

```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start scheduler.js --name kajabi-hubspot

# View logs
pm2 logs kajabi-hubspot

# Restart
pm2 restart kajabi-hubspot

# Stop
pm2 stop kajabi-hubspot

# Auto-start on system boot
pm2 startup
pm2 save
```

### Environment-Specific Configs

Create multiple `.env` files:

- `.env.development`
- `.env.production`

Load based on environment:
```javascript
require('dotenv').config({
  path: `.env.${process.env.NODE_ENV || 'development'}`
});
```

### Webhooks (Future Enhancement)

Instead of polling, use Kajabi webhooks for real-time updates:

1. Create webhook endpoint
2. Configure in Kajabi
3. Process incoming sale events immediately

## Examples

### Run and Save Logs

```bash
npm start 2>&1 | tee sync-$(date +%Y%m%d-%H%M%S).log
```

### Check Last Sync Time

```bash
ls -lt sales_data.xlsx
```

### Count Total Sales

```bash
node -e "
const ExcelJS = require('exceljs');
const workbook = new ExcelJS.Workbook();
workbook.xlsx.readFile('sales_data.xlsx').then(() => {
  const ws = workbook.getWorksheet('Sales');
  console.log('Total sales:', ws.rowCount - 1);
});
"
```

## Best Practices

1. **Test First:** Always run `npm start` once before using scheduler
2. **Monitor Logs:** Check console output regularly for errors
3. **Backup Data:** Keep backups of `sales_data.xlsx`
4. **Rotate Credentials:** Change API keys periodically
5. **Update Dependencies:** Run `npm update` monthly
6. **Review HubSpot:** Verify data accuracy in HubSpot dashboard

## Getting Help

If you encounter issues:

1. Check error messages in console
2. Review [SETUP.md](SETUP.md) troubleshooting section
3. Verify API credentials are valid
4. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
5. Test APIs individually (Kajabi, then HubSpot)
