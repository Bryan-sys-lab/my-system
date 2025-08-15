"""
Data preprocessing for ML training.
Converts raw collector output into structured training data.
"""
import os

def preprocess_text(data):
    print("[ML] Preprocessing text data")
    return data

def preprocess_image(data):
    print("[ML] Preprocessing image data")
    return data

def preprocess_audio(data):
    print("[ML] Preprocessing audio data")
    return data

def save_to_dataset(data, data_type, base_path="data/training"):
    os.makedirs(os.path.join(base_path, data_type), exist_ok=True)
    file_path = os.path.join(base_path, data_type, f"{len(os.listdir(os.path.join(base_path, data_type)))}.dat")
    with open(file_path, "wb") as f:
        if isinstance(data, str):
            data = data.encode()
        f.write(data)
    print(f"[ML] Saved {data_type} data to {file_path}")
