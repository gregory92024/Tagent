# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-01-30 (Current Release)

### Added
- **Email Tracking System** (Phase 2)
  - `src/email_tracking.py` - New EmailTracker class for tracking reminder status
  - `data/email_tracking.json` - JSON storage for tracking data
  - `templates/renewal_reminder.txt` - Email template with personalization placeholders
  - `renewal_cron.sh` - Daily cron script for automated renewal checks
  - `setup_renewal_cron.sh` - Helper script to install cron job

- **Escalating Reminder Sequence**
  - Reminder 1: 18+ months after payment (6 months before renewal)
  - Reminder 2: 21+ months after payment (3 months before renewal)
  - Reminder 3: 23+ months after payment (1 month before renewal)

- **New CLI Commands**
  - `--renewal-check` - Daily check: shows conversions + due reminders
  - `--renewal-send` - Preview emails ready to send with personalized content
  - `--mark-sent ID` - Mark email as sent for subscriber
  - `--mark-response ID` - Mark response received from subscriber

- **Conversion Detection**
  - Tracks contact status: pending → responded → converted → lapsed
  - Kajabi integration for detecting new purchases by tracked contacts

### Changed
- Updated `src/__init__.py` to export `EmailTracker` class
- Bumped version to 1.1.0 in package
- Extended `EmailWorkflow` class with conversion/reminder logic

### Technical Notes
- 189 renewal candidates automatically added to tracking on first check
- Tracking persists across sessions in JSON format
- Cron job runs daily at 6:00 AM, logs to `logs/renewal_cron.log`

---

## [1.2.0] - 2026-01-30

### Added
- `src/email_workflow.py` - New module for renewal candidate identification
- `EmailWorkflow` class with methods:
  - `parse_payment_date()` - Handles various date formats (datetime, strings like "online 5.11.25")
  - `check_exclusions()` - Filters contacts by email validity, COMPETITOR flag, marketing opt-out
  - `get_renewal_candidates()` - Finds contacts 18-24 months since payment
  - `get_status_counts()` - Returns summary counts by renewal status
  - `generate_renewal_report()` - Formatted console output with statistics
  - `print_candidate_list()` - Detailed table of renewal candidates
- New CLI commands in `run.py`:
  - `--renewal-status` - Show renewal status summary counts
  - `--renewal-list` - Show all renewal candidates with details

### Changed
- Updated `src/__init__.py` to export `EmailWorkflow` class
- Renewal cycle configured: 24 months (2 years)
- Reminder window: 18-24 months after payment (6 months before renewal)

### Technical Notes
- Initial run identifies 189 renewal candidates from 1,770 total records
- 219 records excluded due to missing email addresses
- Date parsing handles multiple formats including "online M.D.YY" strings

---

## [1.1.1] - 2026-01-28

### Added
- `EMAIL_AUTOMATION_SETUP.md` - Email automation configuration guide
- `EMAIL_SETUP_TODO.md` - Email setup task tracking
- `EMAIL_WORKFLOW_SYSTEM.md` - Email workflow documentation

### Changed
- Documentation reorganized per audit

---

## [1.1.0] - 2026-01-27

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
