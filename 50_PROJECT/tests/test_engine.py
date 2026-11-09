"""Unit tests for SearchEngine orchestration and threshold evaluation."""
import numpy as np
import pytest
from unittest.mock import MagicMock

from src.engine import SearchEngine, SearchResponse
from src.config import TEXT_EXACT_THRESHOLD, TEXT_SIMILAR_THRESHOLD, TEXT_SEMANTIC_THRESHOLD


def test_search_engine_text_query_formatting():
    # Mock SigLIP2Service
    mock_model = MagicMock()
    mock_model.encode_text.return_value = np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float32)

    # Mock LocalVectorStore returning varied similarity scores
    mock_store = MagicMock()
    mock_store.search.return_value = [
        {
            "asset_id": "1",
            "usd_path": "D:/assets/Chair.usd",
            "thumbnail_path": "D:/assets/Chair.png",
            "category": "Commercial",
            "subcategory": "Conference",
            "filename": "Chair.usd",
            "score": 0.135,  # Exact Match (>= 0.125)
        },
        {
            "asset_id": "2",
            "usd_path": "D:/assets/Table.usd",
            "thumbnail_path": "D:/assets/Table.png",
            "category": "Commercial",
            "subcategory": "Conference",
            "filename": "Table.usd",
            "score": 0.105,  # High Similarity (>= 0.095)
        },
        {
            "asset_id": "3",
            "usd_path": "D:/assets/Desk.usd",
            "thumbnail_path": "D:/assets/Desk.png",
            "category": "Commercial",
            "subcategory": "Office",
            "filename": "Desk.usd",
            "score": 0.080,  # Semantic Match (>= 0.070)
        },
        {
            "asset_id": "4",
            "usd_path": "D:/assets/Pipe.usd",
            "thumbnail_path": "D:/assets/Pipe.png",
            "category": "Industrial",
            "subcategory": "Piping",
            "filename": "Pipe.usd",
            "score": 0.040,  # Low Relevance
        },
    ]

    engine = SearchEngine(model_service=mock_model, vector_store=mock_store)
    res = engine.search_text(prompt="leather office chair", top_k=4)

    assert isinstance(res, SearchResponse)
    assert res.query_type == "text"
    assert res.query_content == "leather office chair"
    assert res.total_results == 4

    # Verify classification threshold logic (ADR-004)
    assert res.results[0].match_type == "Exact Match"
    assert res.results[1].match_type == "High Similarity"
    assert res.results[2].match_type == "Semantic Match"
    assert res.results[3].match_type == "Low Relevance"

