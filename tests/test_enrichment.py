import pytest
from libs.enrichment import hash_index, faiss_index, nlp, ocr, vision_yolov8

def test_hash_index_extremes():
    # Edge: empty file path
    with pytest.raises(Exception):
        hash_index.sha256_file('')
    with pytest.raises(Exception):
        hash_index.phash_file('')

def test_faiss_index_extremes():
    # Edge: empty vectors
    import numpy as np
    with pytest.raises(Exception):
        faiss_index.build_index(np.array([]))

def test_nlp_extract_entities_extremes():
    # Edge: empty text
    assert nlp.extract_entities('') == []

def test_ocr_extremes():
    # Edge: non-existent file
    with pytest.raises(Exception):
        ocr.ocr('notarealfile.png')

def test_vision_yolov8_extremes():
    # Edge: non-existent image
    with pytest.raises(Exception):
        vision_yolov8.detect_objects(['notarealfile.png'])
