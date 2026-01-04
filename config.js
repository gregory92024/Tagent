require('dotenv').config();

module.exports = {
  kajabi: {
    apiKey: process.env.KAJABI_API_KEY,
    apiSecret: process.env.KAJABI_API_SECRET,
    baseUrl: 'https://api.kajabi.com'
  },
  hubspot: {
    accessToken: process.env.HUBSPOT_ACCESS_TOKEN
  },
  excel: {
    fileName: 'sales_data.xlsx',
    sheetName: 'Sales'
  },
  // Poll interval in minutes (for continuous monitoring)
  pollInterval: process.env.POLL_INTERVAL || 5
};
