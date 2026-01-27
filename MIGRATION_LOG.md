# Mac-to-WSL Migration Log

## Migration Summary

| Field | Value |
|-------|-------|
| **Date** | January 24, 2026 |
| **Source** | macOS with paths `/Users/timothysepulvado/...` |
| **Target** | WSL (Windows Subsystem for Linux) with paths `/mnt/c/Users/Gregory/OneDrive/Desktop/...` |

---

## Files Modified (Path Updates)

| File | Changes Made |
|------|--------------|
| `EMAIL_AUTOMATION_SETUP.md` | Source file path updated to WSL path |
| `EMAIL_WORKFLOW_SYSTEM.md` | Source file path updated to WSL path |
| `CRM_integration/SETUP_PLAN.md` | 5 path references updated + cron documentation added |
| `CRM_integration/CONTEXT_HANDOFF.md` | File locations + automation references updated |
| `ADVANCED_TEACHCE_SOURCE_OF_TRUTH.md` | Project folder paths updated |
| `CLAUDE_CODE_SETUP.md` | MS Office MCP paths updated (WSL note added) |
| `teachce-quiz-web/WALKTHROUGH.md` | Navigation path updated |
| `teachce-quiz-web/PROJECT_INVENTORY.md` | 2 project locations updated |
| `live_class_material/split_transcript.py` | Hardcoded paths updated |

---

## Files Created

| File | Purpose |
|------|---------|
| `CRM_integration/setup_cron.sh` | WSL cron configuration script (replaces macOS LaunchAgent) |

---

## Files Deleted

| File | Reason |
|------|--------|
| `CRM_integration/com.teachce.crm-sync.plist` | macOS LaunchAgent - obsolete on WSL |

---

## Key Path Mappings

```
OLD: /Users/timothysepulvado/Teach/...
NEW: /mnt/c/Users/Gregory/OneDrive/Desktop/...

OLD: /Users/timothysepulvado/Downloads/...
NEW: /mnt/c/Users/Gregory/OneDrive/Desktop/CRM_integration/data/...

OLD: ~/Library/Application Support/Claude/
NEW: ~/.claude/
```

---

## WSL-Specific Notes

### MS Office MCPs
- MS Office MCPs are **not available on WSL**
- Use Claude Code's built-in document skills instead (docx, xlsx, pptx)

### Task Scheduling
- **macOS**: LaunchAgent (`.plist` files in `~/Library/LaunchAgents/`)
- **WSL**: Cron (configured via `crontab -e` or `setup_cron.sh`)

### Python Virtual Environment
- macOS venv is **incompatible with WSL** (different Python paths, architecture)
- Must recreate venv on WSL using `python3 -m venv venv`

### Cron Service
WSL may not start cron automatically. To enable:
```bash
# Check status
sudo service cron status

# Start if needed
sudo service cron start

# Optional: Auto-start on WSL boot (add to ~/.bashrc or use systemd)
```

---

## Testing Performed

| Test | Status | Notes |
|------|--------|-------|
| Venv creation | PASS | Created with `--without-pip` workaround, then bootstrapped pip |
| Dependencies install | PASS | All 6 packages installed (dotenv, requests, hubspot, openpyxl, pandas, json-logger) |
| HubSpot setup | PASS | All custom properties verified (credentials, organization, specialty, year_acquired, courses_ordered, subscriber_number) |
| Kajabi auth | PASS | OAuth2 working, fetched 30 orders |
| HubSpot sync | PASS | 437 created, 1107 updated from 1770 records |
| Full pipeline | PASS | Complete run: Kajabi → Excel → HubSpot |
| Bash wrapper | PASS | `./sync.sh kajabi` works correctly |
| Cron service | PASS | Active and running |
| Cron job | PENDING | Run `./setup_cron.sh` to configure scheduled syncs |

---

## Issues Encountered

1. **python3-venv not installed** - WSL Ubuntu required `sudo apt install python3.12-venv`
2. **Workaround needed** - Used `python3 -m venv venv --without-pip` then bootstrapped pip with get-pip.py
3. **HUBSPOT_PORTAL_ID placeholder** - Updated from `your_portal_id_here` to `244737161`
4. **3 invalid emails in data** - Gracefully handled (missing @ symbols, commas instead of periods)

---

## Rollback Notes

If issues occur:
1. Check `.env` credentials are valid (may need rotation)
2. Verify Python version compatibility (`python3 --version`)
3. Check network connectivity for API calls
4. Review logs: `cat logs/sync_*.log | tail -50`
