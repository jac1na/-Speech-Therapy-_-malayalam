import whisper

_model = None

def get_model():
    global _model
    if _model is None:
        # "small" or "medium" gives noticeably better Malayalam accuracy than "base"
        _model = whisper.load_model("small")
    return _model

class WhisperService:
    @staticmethod
    def transcribe(audio_path):
        model = get_model()
        result = model.transcribe(audio_path, language="ml")
        return result["text"], result.get("duration")