from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json
import os

app = FastAPI()

HISTORY_FILE = "data/history.json"

if not os.path.exists(HISTORY_FILE):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump({}, f)

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default_conversation"

def load_history(conversation_id: str):
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f).get(conversation_id, [])
    except Exception:
        return []

def save_history(conversation_id: str, message: str, response: str):
    try:
        with open(HISTORY_FILE, "r") as f:
            all_history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_history = {}
    all_history[conversation_id] = all_history.get(conversation_id, []) + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response}
    ]
    with open(HISTORY_FILE, "w") as f:
        json.dump(all_history, f, indent=2)

@app.post("/chat")
async def chat(request: ChatRequest):
    history = load_history(request.conversation_id)
    messages = history + [{"role": "user", "content": request.message}]
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    payload = {"model": "llama3.2", "messages": messages, "stream": False}
    response = requests.post(f"{ollama_url}/api/chat", json=payload, timeout=30)
    if response.status_code != 200:
        return {"error": "Failed to get response from Ollama"}
    ollama_response = response.json().get("message", {}).get("content", "No response")
    save_history(request.conversation_id, request.message, ollama_response)
    return {"response": ollama_response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)