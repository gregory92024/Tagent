# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-27 (Current Release)

### Added
- Incremental HubSpot sync using data hashing
- `hubspot_sync_state.json` for tracking synced contacts
- `_compute_contact_hash()` function for change detection
- `_is_contact_changed()` and `_mark_contact_synced()` methods
- `force_full` parameter for bypassing incremental logic

### Changed
- HubSpot sync now only processes changed contacts by default
- First run builds initial sync state (processes all contacts once)
- Subsequent runs are significantly faster

---

## [1.0.0] - 2026-01-24

### Added
- Complete Kajabi → Excel → HubSpot pipeline
- OAuth2 authentication for Kajabi API
- HubSpot Personal Access Token authentication
- Email validation with invalid email logging (`logs/invalid_emails.log`)
- 6 custom HubSpot properties (credentials, organization, specialty, year_acquired, courses_ordered, subscriber_number)
- Bash wrapper script (`sync.sh`) for automation
- Cron job setup script (`setup_cron.sh`) for WSL
- CLAUDE.md project guidelines

### Changed
- Migrated from macOS to WSL environment
- Updated file paths for Windows/WSL compatibility

### Fixed
- Email validation to skip invalid addresses
- Individual record failures no longer stop entire sync

---

## [0.1.0] - 2026-01-20

### Added
- Initial project setup
- Basic Kajabi API integration
- Basic HubSpot API integration
- Excel read/write operations
- Modular source structure (`src/` directory)
- Virtual environment setup
- Environment-based configuration

### Security
- API credentials stored in `.env` file
- `.gitignore` configured to protect sensitive data
