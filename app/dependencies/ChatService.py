# dependencies/ChatService.py

import httpx
from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Annotated, List, Dict, Any
import json

class ChatService:
    def __init__(self, ollama_url: str = "http://ollama:11434/api/chat"):
        self.ollama_url = ollama_url

    async def chat_stream(self, model: str, messages: List[Dict[str, Any]]):
        payload = {
            "model": model,
            "messages": [self._msg_to_dict(m) for m in messages],
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(self.ollama_url, json=payload)

            if resp.status_code == 400:
                raise HTTPException(status_code=400, detail="Model not found or not loaded.")
            elif resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Ollama server error.")

            async def event_generator():
                async for line in resp.aiter_lines():
                    if line.strip():
                        yield f"{line}\n"

            return StreamingResponse(event_generator(), media_type="application/x-ndjson")

    async def chat(self, model: str, messages: List[Dict[str, Any]]):
        payload = {
            "model": model,
            "messages": [self._msg_to_dict(m) for m in messages],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(self.ollama_url, json=payload)

            if resp.status_code == 400:
                raise HTTPException(status_code=400, detail="Model not found or not loaded.")
            elif resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Ollama server error.")

            try:
                result = resp.json()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to parse JSON: {repr(e)}")

            return result

    def _msg_to_dict(self, msg):
        if isinstance(msg, dict):
            return msg
        return {
            "role": getattr(msg, "role", "user"),
            "content": getattr(msg, "content", ""),
        }

# Dependency 提供函數
def get_chat_service() -> ChatService:
    return ChatService()

# Annotated for injection
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
