require('dotenv').config();
const axios = require('axios');
const { Client } = require('@hubspot/api-client');
const ExcelJS = require('exceljs');
const path = require('path');

// Initialize HubSpot client
const hubspotClient = new Client({ accessToken: process.env.HUBSPOT_ACCESS_TOKEN });

// Kajabi API configuration
const KAJABI_BASE_URL = 'https://api.kajabi.com';
let kajabiAccessToken = null;

/**
 * Get Kajabi OAuth access token
 */
async function getKajabiAccessToken() {
  if (kajabiAccessToken) {
    return kajabiAccessToken;
  }

  try {
    const params = new URLSearchParams();
    params.append('client_id', process.env.KAJABI_API_KEY);
    params.append('client_secret', process.env.KAJABI_API_SECRET);
    params.append('grant_type', 'client_credentials');

    const response = await axios.post(`${KAJABI_BASE_URL}/v1/oauth/token`, params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    kajabiAccessToken = response.data.access_token;
    console.log('✓ Kajabi OAuth token obtained');
    return kajabiAccessToken;
  } catch (error) {
    console.error('Error getting Kajabi access token:', error.response?.data || error.message);
    throw error;
  }
}

// Excel file path
const EXCEL_FILE_PATH = path.join(__dirname, 'sales_data.xlsx');

/**
 * Fetch recent sales from Kajabi
 */
async function fetchKajabiSales() {
  try {
    console.log('Fetching sales from Kajabi...');

    // Get access token first
    const accessToken = await getKajabiAccessToken();

    const response = await axios.get(`${KAJABI_BASE_URL}/v1/purchases?include=customer,offer`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    // API uses JSON:API format with 'data' array and 'included' relationships
    const purchases = response.data.data || [];
    const included = response.data.included || [];

    // Create lookup maps for customers and offers
    const customersMap = {};
    const offersMap = {};

    included.forEach(item => {
      if (item.type === 'customers') {
        customersMap[item.id] = item.attributes;
      } else if (item.type === 'offers') {
        offersMap[item.id] = item.attributes;
      }
    });

    // Transform JSON:API format to our expected format
    return purchases.map(purchase => {
      const customerId = purchase.relationships?.customer?.data?.id;
      const offerId = purchase.relationships?.offer?.data?.id;
      const customer = customersMap[customerId];
      const offer = offersMap[offerId];

      // Split name into first and last name (best effort)
      let firstName = '';
      let lastName = '';
      if (customer?.name) {
        const nameParts = customer.name.split(' ');
        firstName = nameParts[0] || '';
        lastName = nameParts.slice(1).join(' ') || '';
      }

      return {
        id: purchase.id,
        created_at: purchase.attributes.created_at,
        status: purchase.attributes.deactivated_at ? 'refunded' : 'completed',
        amount: (purchase.attributes.amount_in_cents || 0) / 100, // Convert cents to dollars
        offer_name: offer?.title || 'Unknown Product',
        customer: customer ? {
          email: customer.email || '',
          first_name: firstName,
          last_name: lastName,
          phone: '' // Phone not available in API response
        } : null
      };
    });
  } catch (error) {
    console.error('Error fetching Kajabi sales:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Create or update contact in HubSpot
 */
async function upsertHubSpotContact(customerData) {
  try {
    const contactData = {
      properties: {
        email: customerData.email,
        firstname: customerData.first_name || '',
        lastname: customerData.last_name || '',
        phone: customerData.phone || ''
      }
    };

    // Try to create contact, if exists, update it
    try {
      const contact = await hubspotClient.crm.contacts.basicApi.create(contactData);
      console.log(`Created HubSpot contact: ${customerData.email}`);
      return contact;
    } catch (error) {
      if (error.statusCode === 409) {
        // Contact exists, update it
        const existingContact = await hubspotClient.crm.contacts.searchApi.doSearch({
          filterGroups: [{
            filters: [{
              propertyName: 'email',
              operator: 'EQ',
              value: customerData.email
            }]
          }]
        });

        if (existingContact.results.length > 0) {
          const contactId = existingContact.results[0].id;
          const updated = await hubspotClient.crm.contacts.basicApi.update(contactId, contactData);
          console.log(`Updated HubSpot contact: ${customerData.email}`);
          return updated;
        }
      }
      throw error;
    }
  } catch (error) {
    console.error('Error upserting HubSpot contact:', error.message);
    throw error;
  }
}

/**
 * Create deal in HubSpot
 */
async function createHubSpotDeal(saleData, contactId) {
  try {
    const dealData = {
      properties: {
        dealname: `Kajabi Sale - ${saleData.offer_name || 'Product'}`,
        amount: saleData.amount || 0,
        dealstage: 'closedwon',
        pipeline: 'default',
        closedate: new Date(saleData.created_at).getTime()
      },
      associations: [
        {
          to: { id: contactId },
          types: [{ associationCategory: 'HUBSPOT_DEFINED', associationTypeId: 3 }]
        }
      ]
    };

    const deal = await hubspotClient.crm.deals.basicApi.create(dealData);
    console.log(`Created HubSpot deal for ${saleData.offer_name}`);
    return deal;
  } catch (error) {
    console.error('Error creating HubSpot deal:', error.message);
    throw error;
  }
}

/**
 * Update Excel file with sale data
 */
async function updateExcelFile(salesData) {
  try {
    const workbook = new ExcelJS.Workbook();
    let worksheet;

    // Try to load existing file
    try {
      await workbook.xlsx.readFile(EXCEL_FILE_PATH);
      worksheet = workbook.getWorksheet('Sales');
    } catch (error) {
      // File doesn't exist, create new one
      worksheet = workbook.addWorksheet('Sales');
      worksheet.columns = [
        { header: 'Date', key: 'date', width: 15 },
        { header: 'Customer Name', key: 'name', width: 25 },
        { header: 'Email', key: 'email', width: 30 },
        { header: 'Product', key: 'product', width: 30 },
        { header: 'Amount', key: 'amount', width: 12 },
        { header: 'Status', key: 'status', width: 12 }
      ];
    }

    // Add sales data
    for (const sale of salesData) {
      worksheet.addRow({
        date: new Date(sale.created_at).toLocaleDateString(),
        name: `${sale.customer?.first_name || ''} ${sale.customer?.last_name || ''}`.trim(),
        email: sale.customer?.email || '',
        product: sale.offer_name || 'N/A',
        amount: `$${sale.amount || 0}`,
        status: sale.status || 'completed'
      });
    }

    await workbook.xlsx.writeFile(EXCEL_FILE_PATH);
    console.log(`Excel file updated: ${EXCEL_FILE_PATH}`);
  } catch (error) {
    console.error('Error updating Excel file:', error.message);
    throw error;
  }
}

/**
 * Main integration function
 */
async function runIntegration() {
  try {
    console.log('Starting Kajabi → HubSpot → Excel integration...\n');

    // Step 1: Fetch sales from Kajabi
    const sales = await fetchKajabiSales();
    console.log(`Found ${sales.length} sales from Kajabi\n`);

    if (sales.length === 0) {
      console.log('No sales to process.');
      return;
    }

    // Step 2 & 3: Process each sale
    for (const sale of sales) {
      try {
        console.log(`Processing sale: ${sale.id}`);

        // Create/update contact in HubSpot
        if (sale.customer) {
          const contact = await upsertHubSpotContact(sale.customer);

          // Create deal in HubSpot
          if (contact) {
            await createHubSpotDeal(sale, contact.id);
          }
        }
      } catch (error) {
        console.error(`Error processing sale ${sale.id}:`, error.message);
        // Continue with other sales
      }
    }

    // Step 4: Update Excel file
    await updateExcelFile(sales);

    console.log('\n✓ Integration completed successfully!');
  } catch (error) {
    console.error('Integration failed:', error.message);
    process.exit(1);
  }
}

// Run the integration
if (require.main === module) {
  runIntegration();
}

module.exports = { runIntegration, fetchKajabiSales, upsertHubSpotContact, createHubSpotDeal, updateExcelFile };
