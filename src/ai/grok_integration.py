import requests
import json

class GrokClient:
    def __init__(self, api_key: str, model: str = "grok-3-mini-beta"):
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://api.groq.com/v1/chat/completions"

    def ask(self, prompt: str, system: str = "You are an NPC in a gothic investigation game.") -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[Grok Error] {e}"
