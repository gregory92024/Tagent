# TeachCE CRM Integration
# Syncs Kajabi orders with HubSpot CRM and Excel tracking

from .kajabi_client import KajabiClient
from .hubspot_client import HubSpotClient
from .excel_sync import ExcelSync
from .sync_pipeline import SyncPipeline
from .email_workflow import EmailWorkflow
from .email_tracking import EmailTracker

__version__ = "1.1.0"
__all__ = [
    "KajabiClient",
    "HubSpotClient",
    "ExcelSync",
    "SyncPipeline",
    "EmailWorkflow",
    "EmailTracker",
]
