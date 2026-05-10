import re

def detect_prompt_injection(text: str) -> bool:
    """
    Basic heuristic-based prompt injection detection.
    In production, use a dedicated LLM or a library like Lakera.
    """
    if not text:
        return False
        
    suspicious_patterns = [
        r"ignore previous instructions",
        r"disregard all previous",
        r"you are now a",
        r"system prompt",
        r"bypass",
        r"print your instructions",
        r"reveal your instructions"
    ]
    
    text_lower = text.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, text_lower):
            return True
            
    return False
