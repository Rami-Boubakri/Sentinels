import os
import requests

def generate_completion(
    prompt: str,
    system_prompt: str = "You are a helpful banking assistant.",
    model: str = "llama-3.3-70b-versatile"
) -> str:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        return "Error: GROQ_API_KEY not set."

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 1024
            },
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[LLM] Groq failed: {type(e).__name__}: {e}")
        return f"Error: Unable to generate analysis. {e}"
