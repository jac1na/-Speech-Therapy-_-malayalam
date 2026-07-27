# speech/services/feedback_service.py

class FeedbackService:
    @staticmethod
    def generate(score):
        if score > 90:
            return "മികച്ചത്! ഉച്ചാരണം വളരെ നല്ലതാണ്."  # Excellent pronunciation
        elif score >= 80:
            return "വളരെ നല്ലത്. കുറച്ചുകൂടി പരിശീലിക്കുക."  # Very good, practice a bit more
        elif score >= 60:
            return "മെച്ചപ്പെടുത്തേണ്ടതുണ്ട്. വീണ്ടും ശ്രമിക്കുക."  # Needs improvement
        else:
            return "ദയവായി വ്യായാമം ആവർത്തിക്കുക."  # Please repeat the exercise