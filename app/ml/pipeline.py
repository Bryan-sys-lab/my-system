"""
Pipeline that listens to enriched data and feeds it to preprocessing + dataset storage.
"""
from app.ml import preprocess

def on_new_enriched_data(data_type, data):
    """
    Called whenever new enriched data is available from collectors.
    data_type: "text", "image", "audio", "video"
    data: raw data content
    """
    print(f"[ML] Received new {data_type} data for training pipeline")
    
    if data_type == "text":
        processed = preprocess.preprocess_text(data)
    elif data_type == "image":
        processed = preprocess.preprocess_image(data)
    elif data_type == "audio":
        processed = preprocess.preprocess_audio(data)
    else:
        processed = data
    
    preprocess.save_to_dataset(processed, data_type)
