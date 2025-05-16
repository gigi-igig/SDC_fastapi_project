from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from model.Interfaces import ChatResponse, ChatRequest,CreateMessageRequest
from dependencies.SessionData import SessionServiceDep
from dependencies.MessageData import MessageServiceDep
import httpx
import asyncio
import json

router = APIRouter(prefix="/chat")


@router.post("/", response_model=Optional[ChatResponse])
async def chat_with_model(
    body: ChatRequest,
    service: SessionServiceDep,
    message_service: MessageServiceDep,
    session_id: Optional[int] = Query(default=None),
):
    if session_id:
        session_obj = service.read_single_session(session_id)
        if not session_obj : #or not getattr(session_obj, "messages", None)
            raise HTTPException(status_code=404, detail="Session ID not found.")
        
        history = message_service.get_messages(session_id)
        history_messages = [ChatResponse(role=msg.role, content=msg.content) for msg in history]
        all_messages = history_messages + body.messages
    else:
        all_messages = body.messages

    payload = {
        "model": body.model,
        "messages": [msg.to_dict() for msg in all_messages],
        "stream": body.stream,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post("http://ollama:11434/api/chat", json=payload)

            if resp.status_code == 400:
                raise HTTPException(status_code=400, detail="Model not found or not loaded.")
            elif resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Ollama server error.")

            if body.stream:
                async def stream_response():
                    async for line in resp.aiter_lines():
                        if line.strip():
                            yield f"{line}\n"
                return StreamingResponse(stream_response(), media_type="application/x-ndjson")
            else:
                try:
                    result = resp.json() #"object dict can't be used in 'await' expression\"
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to parse JSON: {repr(e)}")
                assistant_msg = result.get("message")

                
                if session_id and assistant_msg:
                    for msg in body.messages:
                        user_msg = CreateMessageRequest(
                            content=msg.content,
                            role=msg.role,
                            session_id=session_id
                        )
                        message_service.add_message(user_msg)
                    message_to_add = CreateMessageRequest(
                        content=assistant_msg["content"],
                        role=assistant_msg.get("role", "assistant"),
                        session_id=session_id
                    )
                    message_service.add_message(message_to_add)
                

                return JSONResponse(content=result)

    except httpx.RequestError as e:
        raise HTTPException(status_code=404, detail=f"Error communicating with Ollama server: {repr(e)}")
