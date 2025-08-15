from PIL import Image
import pytesseract

def image_to_text(path: str) -> str:
    img = Image.open(path)
    return pytesseract.image_to_string(img)
