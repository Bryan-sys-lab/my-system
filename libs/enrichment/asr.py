import whisper

def transcribe(path: str, model_name: str = "base"):
    model = whisper.load_model(model_name)
    return model.transcribe(path)
