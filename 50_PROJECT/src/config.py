"""Configuration parameters for ID-104 USD Multimodal Search Engine."""
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_USD_DIR = Path(r"D:\___tmp\USD_assets")
QDRANT_STORAGE_DIR = PROJECT_ROOT / "data" / "qdrant_db"

# Model Configuration
DEFAULT_MODEL_NAME = "google/siglip2-base-patch16-224"
VECTOR_DIM = 768
QDRANT_COLLECTION_NAME = "usd_assets_siglip2"

# SigLIP 2 Model Constants
LOGIT_SCALE = 112.6689
LOGIT_BIAS = -16.7717

# Similarity Thresholds (ADR-004)
# For Image-to-Image (direct Cosine Similarity):
IMAGE_EXACT_THRESHOLD = 0.82
IMAGE_SIMILAR_THRESHOLD = 0.65

# For Text-to-Image (SigLIP 2 Cosine Similarity range is ~0.08 - 0.20):
TEXT_EXACT_THRESHOLD = 0.125
TEXT_SIMILAR_THRESHOLD = 0.095
TEXT_SEMANTIC_THRESHOLD = 0.070

# Supported Extensions
USD_EXTENSIONS = {".usd", ".usda", ".usdc"}
THUMB_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
