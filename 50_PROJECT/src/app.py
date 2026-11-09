"""Streamlit Web Dashboard for ID-104 USD Multimodal Search Engine."""
import os
import sys
from pathlib import Path

# Ensure 50_PROJECT is in sys.path so imports like `from src.config` work under Streamlit
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from PIL import Image

# Setup page layout
st.set_page_config(
    page_title="USD Multimodal Search | SigLIP 2",
    page_icon="🔍",
    layout="wide",
)

from src.config import (
    DEFAULT_USD_DIR,
    IMAGE_EXACT_THRESHOLD,
    IMAGE_SIMILAR_THRESHOLD,
    TEXT_EXACT_THRESHOLD,
    TEXT_SIMILAR_THRESHOLD,
    QDRANT_STORAGE_DIR,
)
from src.engine import SearchEngine
from src.model_service import SigLIP2Service
from src.scanner import AssetScanner
from src.vector_store import LocalVectorStore


@st.cache_resource
def get_search_engine():
    model = SigLIP2Service()
    store = LocalVectorStore()
    return SearchEngine(model_service=model, vector_store=store), store


def main():
    st.title("🔍 OpenUSD Multimodal Asset Search Engine")
    st.caption("Powered by **Google SigLIP 2** & **Embedded Qdrant** (100% Local Workstation Execution)")

    try:
        engine, store = get_search_engine()
        total_indexed = store.count()
    except Exception as e:
        st.error(f"Error initializing local engine: {e}")
        st.stop()

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Settings & Database")
        st.metric(label="Total USD Assets Indexed", value=total_indexed)

        category_filter = st.selectbox(
            "Category Filter",
            options=["All", "Commercial", "Industrial", "Residential"],
            index=0,
        )

        top_k = st.slider("Max Results (Top-K)", min_value=1, max_value=25, value=8)

        st.markdown("---")
        st.markdown("### 📊 Confidence Thresholds (ADR-004)")
        st.write(f"- 🟢 **Exact Match:** $\\ge {TEXT_EXACT_THRESHOLD}$ (Text) / $\\ge {IMAGE_EXACT_THRESHOLD}$ (Image)")
        st.write(f"- 🔵 **High Similarity:** $\\ge {TEXT_SIMILAR_THRESHOLD}$ (Text) / $\\ge {IMAGE_SIMILAR_THRESHOLD}$ (Image)")
        st.write("- 🟡 **Semantic Match:** Lower relevance")

        st.markdown("---")
        st.markdown(f"**Local Vector DB Path:**\n`{QDRANT_STORAGE_DIR}`")

    # Search tabs: Text vs Image
    tab_text, tab_image = st.tabs(["💬 Search by Text Prompt", "🖼️ Search by Reference Image"])

    results = None
    query_display = ""

    with tab_text:
        with st.form("text_search_form"):
            query_text = st.text_input(
                "Enter natural language query",
                placeholder="e.g. leather conference table, industrial electrical transformer, modern desk...",
            )
            submitted_text = st.form_submit_button("Search Catalog")

        if submitted_text and query_text.strip():
            query_display = f"Text: *'{query_text}'*"
            with st.spinner("Executing SigLIP 2 inference & cosine nearest-neighbor search..."):
                results = engine.search_text(
                    prompt=query_text.strip(),
                    top_k=top_k,
                    category=category_filter,
                )

    with tab_image:
        uploaded_file = st.file_uploader(
            "Upload reference image",
            type=["png", "jpg", "jpeg", "webp"],
            help="Drag and drop any 2D photo or rendered frame to find identical or visually similar USD 3D assets.",
        )
        if uploaded_file is not None:
            col_preview, col_btn = st.columns([1, 3])
            with col_preview:
                image = Image.open(uploaded_file)
                st.image(image, caption="Query Reference Image", use_container_width=True)
            with col_btn:
                st.write("")
                st.write("")
                search_img_btn = st.button("Search Using This Image")

            if search_img_btn:
                # Save temp query image
                temp_path = Path("50_PROJECT/data") / f"query_{uploaded_file.name}"
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(temp_path)
                query_display = f"Reference Image: *{uploaded_file.name}*"
                with st.spinner("Extracting visual features via SigLIP 2..."):
                    results = engine.search_image(
                        image_path=str(temp_path),
                        top_k=top_k,
                        category=category_filter,
                    )

    # Render results grid
    if results is not None:
        st.markdown("---")
        st.subheader(f"Results for {query_display}")
        st.caption(f"Retrieved {results.total_results} matching 3D assets.")

        if not results.results:
            st.warning("No matching assets found for this query and category filter.")
        else:
            cols = st.columns(4)
            for idx, item in enumerate(results.results):
                with cols[idx % 4]:
                    # Thumbnail image
                    if Path(item.thumbnail_path).exists():
                        st.image(item.thumbnail_path, use_container_width=True)
                    else:
                        st.text("[No Thumbnail Available]")

                    # Confidence badge
                    if item.match_type == "Exact Match":
                        badge_color = "🟢"
                    elif item.match_type == "High Similarity":
                        badge_color = "🔵"
                    else:
                        badge_color = "🟡"

                    st.markdown(f"**{item.filename}**")
                    st.markdown(f"{badge_color} **{item.match_type}** (`{item.score * 100:.1f}%`)")
                    st.caption(f"📁 {item.category} / {item.subcategory}")

                    with st.expander("USD File Path"):
                        st.code(item.usd_path, language="text")


if __name__ == "__main__":
    main()

