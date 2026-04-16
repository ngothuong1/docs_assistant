import requests

res = requests.post(
    "http://localhost:11434/api/embed",
    json={
        "model": "embeddinggemma",
        "input": "Hướng dẫn đăng nhập VPN",
    },
    timeout=60,
)

data = res.json()
print(type(data["embeddings"]))
print(len(data["embeddings"][0]))