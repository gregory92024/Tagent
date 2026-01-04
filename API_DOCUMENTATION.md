# API Documentation

Technical documentation for the Kajabi and HubSpot API integrations

## Kajabi API

### Base URL
```
https://api.kajabi.com
```

### Authentication
Uses Bearer token authentication with API Key and Secret.

**Headers:**
```javascript
{
  'Authorization': 'Bearer YOUR_API_KEY',
  'Content-Type': 'application/json'
}
```

### Endpoints Used

#### Get Purchases
```
GET /v1/purchases
```

**Response Format:**
```json
{
  "purchases": [
    {
      "id": "purchase_id",
      "created_at": "2026-01-03T12:00:00Z",
      "status": "completed",
      "amount": 99.99,
      "offer_name": "Product Name",
      "customer": {
        "email": "customer@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890"
      }
    }
  ]
}
```

### Rate Limits
- Check Kajabi documentation for current limits
- Implement exponential backoff if needed

## HubSpot API

### Authentication
Uses Personal Access Token (PAT) authentication.

**SDK Initialization:**
```javascript
const { Client } = require('@hubspot/api-client');
const hubspotClient = new Client({
  accessToken: 'YOUR_ACCESS_TOKEN'
});
```

### Endpoints Used

#### 1. Create Contact
```javascript
hubspotClient.crm.contacts.basicApi.create({
  properties: {
    email: "customer@example.com",
    firstname: "John",
    lastname: "Doe",
    phone: "+1234567890"
  }
})
```

#### 2. Search Contact
```javascript
hubspotClient.crm.contacts.searchApi.doSearch({
  filterGroups: [{
    filters: [{
      propertyName: 'email',
      operator: 'EQ',
      value: 'customer@example.com'
    }]
  }]
})
```

#### 3. Update Contact
```javascript
hubspotClient.crm.contacts.basicApi.update(contactId, {
  properties: {
    firstname: "John",
    lastname: "Doe"
  }
})
```

#### 4. Create Deal
```javascript
hubspotClient.crm.deals.basicApi.create({
  properties: {
    dealname: "Kajabi Sale - Product Name",
    amount: 99.99,
    dealstage: "closedwon",
    pipeline: "default",
    closedate: Date.now()
  },
  associations: [{
    to: { id: contactId },
    types: [{
      associationCategory: 'HUBSPOT_DEFINED',
      associationTypeId: 3
    }]
  }]
})
```

### Association Types
- **Contact to Deal:** `associationTypeId: 3`
- See HubSpot documentation for other association types

### Deal Stages
- `closedwon` - Successfully closed sale
- `closedlost` - Lost opportunity
- Custom stages based on your pipeline

## Excel Export

### Library
Uses `exceljs` for Excel file operations.

### File Structure
```
Sales Worksheet
├── Date (Column A)
├── Customer Name (Column B)
├── Email (Column C)
├── Product (Column D)
├── Amount (Column E)
└── Status (Column F)
```

### Operations

#### Read Existing File
```javascript
const workbook = new ExcelJS.Workbook();
await workbook.xlsx.readFile(filePath);
```

#### Create New Worksheet
```javascript
const worksheet = workbook.addWorksheet('Sales');
worksheet.columns = [
  { header: 'Date', key: 'date', width: 15 },
  { header: 'Customer Name', key: 'name', width: 25 },
  // ... other columns
];
```

#### Add Rows
```javascript
worksheet.addRow({
  date: '01/03/2026',
  name: 'John Doe',
  email: 'john@example.com',
  product: 'Product Name',
  amount: '$99.99',
  status: 'completed'
});
```

#### Save File
```javascript
await workbook.xlsx.writeFile(filePath);
```

## Error Handling

### Kajabi Errors
```javascript
try {
  const response = await axios.get(url, { headers });
} catch (error) {
  console.error('Kajabi API Error:', error.response?.data || error.message);
}
```

### HubSpot Errors
```javascript
try {
  await hubspotClient.crm.contacts.basicApi.create(data);
} catch (error) {
  if (error.statusCode === 409) {
    // Contact already exists - update instead
  }
  console.error('HubSpot API Error:', error.message);
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict (duplicate)
- `429` - Rate Limit Exceeded
- `500` - Server Error

## Best Practices

1. **Rate Limiting**
   - Implement delays between bulk operations
   - Use exponential backoff on failures

2. **Error Recovery**
   - Log all errors with context
   - Continue processing other records on individual failures
   - Implement retry logic for transient errors

3. **Data Validation**
   - Validate email formats
   - Check required fields before API calls
   - Sanitize input data

4. **Security**
   - Never log API keys
   - Use environment variables
   - Rotate credentials regularly
