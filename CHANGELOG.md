# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-01-05

### Added
- Date-based filtering for purchases via `PURCHASE_CUTOFF_DATE` environment variable
- Only processes purchases created after the specified cutoff date
- Automatic timezone display (PST) for cutoff date in logs
- Filter statistics showing how many purchases were filtered vs processed

### Changed
- Integration now skips historical data and only syncs new purchases
- Default cutoff set to January 5, 2026 00:00:00 PST (2026-01-05T08:00:00Z)

## [0.2.1] - 2026-01-05

### Fixed
- Duplicate contact handling now properly updates existing contacts instead of throwing errors
- Added nested try-catch for 409 conflict resolution
- Contact search and update now returns the updated contact object correctly
- Integration no longer fails when processing duplicate customer emails

## [0.2.0] - 2026-01-05

### Added
- OAuth2 authentication support for Kajabi API
- JSON:API format support with included relationships (customer, offer)
- Automatic mapping of Kajabi purchase data to internal format
- Support for HubSpot Personal Access Token (PAT) authentication
- Excel export functionality for all sales data

### Changed
- Updated Kajabi API integration to use `/v1/oauth/token` endpoint
- Modified purchase data fetching to include customer and offer relationships
- Updated data transformation to handle JSON:API format
- Converted `amount_in_cents` to dollars for HubSpot and Excel
- Split customer `name` field into `first_name` and `last_name`

### Fixed
- API response structure updated from `response.data.purchases` to `response.data.data`
- Added proper relationship mapping for customers and offers
- Status field now checks `deactivated_at` to determine refund status

### Known Issues
- Duplicate contact handling throws 409 errors instead of updating existing contacts
- No date filtering - processes all purchases every run

## [0.1.0] - 2026-01-03

### Added
- Initial project setup
- Basic Kajabi API integration
- Basic HubSpot CRM integration
- Excel export functionality
- Scheduler for continuous monitoring
- Environment-based configuration
- Documentation (README, SETUP, API_DOCUMENTATION, USAGE)

### Security
- API credentials stored in `.env` file
- `.gitignore` configured to protect sensitive data
