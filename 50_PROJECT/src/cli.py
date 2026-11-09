"""CLI Runner for ID-104 USD Multimodal Search Engine."""
import argparse
import sys
import time
from pathlib import Path

# Ensure 50_PROJECT is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import DEFAULT_MODEL_NAME, DEFAULT_USD_DIR, QDRANT_STORAGE_DIR
from src.engine import SearchEngine
from src.model_service import SigLIP2Service
from src.scanner import AssetScanner
from src.vector_store import LocalVectorStore


def cmd_index(args):
    target_dir = Path(args.target) if args.target else DEFAULT_USD_DIR
    print(f"\n[1/3] Scanning USD assets in: {target_dir}")
    scanner = AssetScanner(root_dir=str(target_dir))
    records = scanner.scan()
    print(f"      Discovered {len(records)} USD assets with valid thumbnails.")

    if not records:
        print("      No assets found to index. Check target directory path.")
        return

    print(f"\n[2/3] Loading SigLIP 2 model ({DEFAULT_MODEL_NAME})...")
    t0 = time.time()
    model = SigLIP2Service()
    print(f"      Model loaded on device: {model.device} ({time.time() - t0:.2f}s)")

    print(f"\n[3/3] Encoding thumbnails and indexing in embedded Qdrant ({QDRANT_STORAGE_DIR})...")
    t1 = time.time()
    thumb_paths = [r.thumbnail_path for r in records]
    
    # Batch encoding
    batch_size = args.batch_size
    embeddings_list = []
    for i in range(0, len(thumb_paths), batch_size):
        batch = thumb_paths[i:i + batch_size]
        from PIL import Image
        images = [Image.open(p) for p in batch]
        embs = model.encode_image(images)
        embeddings_list.append(embs)
        print(f"      Processed {min(i + batch_size, len(thumb_paths))}/{len(thumb_paths)} thumbnails...")

    import numpy as np
    all_embeddings = np.vstack(embeddings_list)

    store = LocalVectorStore()
    if args.clear:
        print("      Clearing existing index as requested (--clear)...")
        store.clear()

    count = store.upsert_records(records, all_embeddings)
    elapsed = time.time() - t1
    print(f"\n[SUCCESS] Successfully indexed {count} USD assets in {elapsed:.2f}s.")
    print(f"          Total assets in database: {store.count()}")


def cmd_search_text(args):
    print(f"\nExecuting text search: '{args.query}' (Category: {args.category or 'All'}, Top-K: {args.top_k})")
    model = SigLIP2Service()
    store = LocalVectorStore()
    engine = SearchEngine(model_service=model, vector_store=store)

    t0 = time.time()
    res = engine.search_text(prompt=args.query, top_k=args.top_k, category=args.category)
    elapsed = time.time() - t0

    print(f"Found {res.total_results} matches in {elapsed * 1000:.1f}ms:\n")
    _print_results(res.results)


def cmd_search_image(args):
    img_path = Path(args.image)
    if not img_path.exists():
        print(f"Error: Query image not found at {img_path}")
        return

    print(f"\nExecuting image search: {img_path.name} (Category: {args.category or 'All'}, Top-K: {args.top_k})")
    model = SigLIP2Service()
    store = LocalVectorStore()
    engine = SearchEngine(model_service=model, vector_store=store)

    t0 = time.time()
    res = engine.search_image(image_path=str(img_path), top_k=args.top_k, category=args.category)
    elapsed = time.time() - t0

    print(f"Found {res.total_results} matches in {elapsed * 1000:.1f}ms:\n")
    _print_results(res.results)


def _print_results(results):
    for i, item in enumerate(results, start=1):
        badge = f"[{item.match_type}]"
        print(f"{i}. {badge} Score: {item.score:.4f} | {item.filename} ({item.category}/{item.subcategory})")
        print(f"   USD Path:   {item.usd_path}")
        print(f"   Thumbnail:  {item.thumbnail_path}")
        print()


def main():
    parser = argparse.ArgumentParser(description="ID-104 USD Multimodal Search Engine CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Index command
    p_index = subparsers.add_parser("index", help="Index USD asset library")
    p_index.add_argument("--target", type=str, default=str(DEFAULT_USD_DIR), help="Target USD root folder")
    p_index.add_argument("--batch-size", type=int, default=16, help="Batch size for embedding calculation")
    p_index.add_argument("--clear", action="store_true", help="Clear collection before indexing")
    p_index.set_defaults(func=cmd_index)

    # Search text command
    p_stext = subparsers.add_parser("search-text", help="Search USD assets using natural language text")
    p_stext.add_argument("query", type=str, help="Text query string")
    p_stext.add_argument("--top-k", type=int, default=5, help="Number of results to retrieve")
    p_stext.add_argument("--category", type=str, default=None, help="Filter by category (Commercial, Industrial, etc.)")
    p_stext.set_defaults(func=cmd_search_text)

    # Search image command
    p_simg = subparsers.add_parser("search-image", help="Search USD assets using a reference image")
    p_simg.add_argument("image", type=str, help="Path to reference image")
    p_simg.add_argument("--top-k", type=int, default=5, help="Number of results to retrieve")
    p_simg.add_argument("--category", type=str, default=None, help="Filter by category")
    p_simg.set_defaults(func=cmd_search_image)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

