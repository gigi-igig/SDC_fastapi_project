from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from model.Interfaces import ChatResponse, ChatRequest
from dependencies.SessionData import SessionServiceDep
import httpx
import asyncio
import json

router = APIRouter(prefix="/chat")


@router.post("/", response_model=Optional[ChatResponse])
async def chat_with_model(
    body: ChatRequest,
    service: SessionServiceDep,
    session_id: Optional[int] = Query(default=None),
):
    history = []
    if session_id is not None:
        session_obj = service.read_single_session(session_id)
        if session_obj is None:
            raise HTTPException(status_code=404, detail="Session ID not found.")
        
        try:
            history = json.loads(session_obj.messages)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to parse session messages.")
        
        body.messages = [ChatResponse(**msg) for msg in history] + body.messages

    payload = {
        "model": body.model,
        "messages": [msg.dict() for msg in body.messages],
        "stream": body.stream,
    }

    ollama_url = "http://ollama_container:11434/api/chat"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(ollama_url, json=payload)

            if resp.status_code == 400:
                raise HTTPException(status_code=400, detail="Model not found or not loaded.")
            elif resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Ollama server error.")

            if body.stream:
                # NOTE: 無法串流過程儲存回 DB，僅適用於非 stream 模式做更新
                async def stream_response():
                    async for line in resp.aiter_lines():
                        if line.strip():
                            yield f"{line}\n"

                return StreamingResponse(stream_response(), media_type="application/x-ndjson")
            else:
                result = resp.json()
                assistant_msg = result.get("message")

                if session_id is not None and assistant_msg:
                    # 新增最新對話內容
                    updated_history = body.messages + [assistant_msg]
                    service.update_messages(session_id, updated_history)

                return JSONResponse(content=result)

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Ollama server: {repr(e)}"
        )