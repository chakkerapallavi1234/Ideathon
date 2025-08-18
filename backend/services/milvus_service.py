# backend/services/milvus_service.py
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from backend.config import settings
import numpy as np
import logging
import time

MILVUS_COLLECTION = "incident_embeddings"
DIM = 1536  # choose embedding dim to match your embedding model

_milvus_connected = False

def get_connection(retries=3, delay=5):
    """Establish a connection to Milvus with retry logic."""
    global _milvus_connected
    if _milvus_connected:
        return

    for attempt in range(retries):
        try:
            connections.connect(alias="default", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)
            _milvus_connected = True
            logging.info("Successfully connected to Milvus.")
            return
        except Exception as e:
            logging.error(f"Failed to connect to Milvus on attempt {attempt + 1}/{retries}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    _milvus_connected = False

def ensure_collection():
    get_connection()
    if not _milvus_connected:
        logging.error("Cannot ensure Milvus collection, no connection.")
        return None
    if utility.has_collection(MILVUS_COLLECTION):
        return Collection(MILVUS_COLLECTION)
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIM),
    ]
    schema = CollectionSchema(fields, description="Incident embeddings")
    collection = Collection(MILVUS_COLLECTION, schema)
    # create index example
    collection.create_index(field_name="embedding", index_params={"index_type":"HNSW","metric_type":"L2","params":{"M":8,"efConstruction":64}})
    collection.load()
    return collection

def upsert_embedding(incident_id: str, text: str):
    """Compute embedding and upsert into Milvus."""
    get_connection()
    collection = ensure_collection()
    if not collection:
        return None
    
    # For PoC: create random vector. Replace with a real embedding model in production.
    vec = np.random.rand(DIM).astype(np.float32).tolist()
    
    # Milvus requires a unique integer ID. We can derive one from the incident ID.
    # Note: This hashing approach is simple but could have collisions.
    # A more robust system might use a dedicated ID mapping service.
    id_int = abs(hash(incident_id)) % (10**12)
    
    try:
        collection.insert([[id_int], [vec]])
        logging.info(f"Successfully upserted embedding for incident {incident_id} into Milvus.")
        return id_int
    except Exception as e:
        logging.error(f"Failed to upsert embedding for incident {incident_id}: {e}")
        return None
