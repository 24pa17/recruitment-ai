import requests
from config.settings import EMBED_URL

def get_embedding(text):
    res = requests.post(EMBED_URL, json={
        "model": "nomic-embed-text",
        "prompt": text
    })
    return res.json()["embedding"]