from typing import List, Dict, Any
import os

def detect_objects(image_paths: List[str], model_name: str = "yolov8n.pt", conf: float = 0.25) -> List[Dict[str, Any]]:
    try:
        from ultralytics import YOLO
    except Exception as e:
        raise RuntimeError("ultralytics not installed") from e
    model = YOLO(model_name)
    outs = []
    for p in image_paths:
        res = model.predict(p, conf=conf, verbose=False)
        # Extract minimal, serializable detections
        parsed = []
        for r in res:
            boxes = r.boxes
            for b in boxes:
                xyxy = b.xyxy[0].tolist()
                cls = int(b.cls[0].item())
                confv = float(b.conf[0].item())
                parsed.append({"bbox": xyxy, "cls": cls, "conf": confv})
        outs.append({"image": p, "detections": parsed})
    return outs
