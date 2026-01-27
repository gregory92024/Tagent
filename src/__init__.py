# TeachCE CRM Integration
# Syncs Kajabi orders with HubSpot CRM and Excel tracking

from .kajabi_client import KajabiClient
from .hubspot_client import HubSpotClient
from .excel_sync import ExcelSync
from .sync_pipeline import SyncPipeline

__version__ = "1.0.0"
__all__ = ["KajabiClient", "HubSpotClient", "ExcelSync", "SyncPipeline"]
