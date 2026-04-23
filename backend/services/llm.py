import requests
from config.settings import OLLAMA_URL

def call_llm(prompt):
    res = requests.post(OLLAMA_URL, json={
        "model": "mistral:7b",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    })
    return res.json()["message"]["content"]