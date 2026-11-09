"""Smoke test script for ID-104 local environment."""
import sys
from pathlib import Path

# Ensure 50_PROJECT is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

def main():
    print("========================================")
    print("ID-104 Environment Smoke Test")
    print("========================================")
    print(f"Python executable: {sys.executable}")
    print(f"Python version:    {sys.version.split()[0]}")

    # 1. PyTorch & CUDA Check
    try:
        import torch
        print(f"PyTorch version:   {torch.__version__}")
        cuda_ok = torch.cuda.is_available()
        print(f"CUDA available:    {cuda_ok}")
        if cuda_ok:
            print(f"GPU device:        {torch.cuda.get_device_name(0)}")
            print(f"VRAM total:        {torch.cuda.get_device_properties(0).total_memory / (1024**2):.0f} MB")
        else:
            print("[WARN] CUDA not detected. Will run in CPU fallback.")
    except Exception as e:
        print(f"[FAIL] PyTorch check: {e}")
        sys.exit(1)

    # 2. Transformers Check
    try:
        import transformers
        print(f"Transformers:      {transformers.__version__}")
    except Exception as e:
        print(f"[FAIL] Transformers check: {e}")
        sys.exit(1)

    # 3. Embedded Qdrant Client Check
    try:
        import qdrant_client
        client = qdrant_client.QdrantClient(location=":memory:")
        collections = client.get_collections()
        print(f"Embedded Qdrant:   OPERATIONAL (in-memory test verified)")
    except Exception as e:
        print(f"[FAIL] Qdrant Client check: {e}")
        sys.exit(1)

    # 4. Project Config & Target USD Directory Check
    try:
        from src.config import DEFAULT_USD_DIR, QDRANT_STORAGE_DIR
        print(f"Config module:     LOADED")
        print(f"Target USD dir:    {DEFAULT_USD_DIR} (Exists: {DEFAULT_USD_DIR.exists()})")
        print(f"Qdrant data dir:   {QDRANT_STORAGE_DIR}")
    except Exception as e:
        print(f"[FAIL] Config import: {e}")
        sys.exit(1)

    print("========================================")
    print("ALL ENVIRONMENT CHECKS PASSED [OK]")
    print("========================================")

if __name__ == "__main__":
    main()
