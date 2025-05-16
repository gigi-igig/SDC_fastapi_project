from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from model.Interfaces import ChatResponse, ChatRequest,CreateMessageRequest
from dependencies.SessionData import SessionServiceDep
from dependencies.MessageData import MessageServiceDep
from dependencies.ChatService import ChatServiceDep
import httpx


router = APIRouter(prefix="/chat")


@router.post("/", response_model=Optional[ChatResponse])
async def chat_with_model(
    body: ChatRequest,
    service: SessionServiceDep,
    message_service: MessageServiceDep,
    chat_service: ChatServiceDep,
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

    # 2. 呼叫 ChatService 與 Ollama 互動
    try:
        if body.stream:
            # 串流回應
            return await chat_service.chat_stream(
                model=body.model,
                messages=all_messages,
            )
        else:
            # 非串流回應
            result = await chat_service.chat(
                model=body.model,
                messages=all_messages,
            )

            assistant_msg = result.get("message")

            # 3. 若有 session_id，將 user 訊息和 assistant 回覆存入 DB
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service error: {repr(e)}")