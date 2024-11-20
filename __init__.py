from .database_query_same_energy import IPAdapterSameEnergy
from .megamergeSDXL import MegaMergeSDXL

NODE_CLASS_MAPPINGS = {
    "IPAdapterSameEnergy": IPAdapterSameEnergy,
    "MegaMergeSDXL": MegaMergeSDXL,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IPAdapterSameEnergy": "IPAdapter (Same.Energy)",
    "MegaMergeSDXL": "MegaMergeSDXL",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
