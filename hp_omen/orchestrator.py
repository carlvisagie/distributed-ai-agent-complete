"""
HP OMEN Orchestrator - Command Center for Distributed AI Agent System
Coordinates tasks between chat interface and Predator Helios worker
"""
import asyncio
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import AsyncGenerator
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HP OMEN Orchestrator", version="1.0.0")

# Configuration
HELIOS_WORKER_URL = "http://predator-helios:9000"  # WebSocket worker
LENOVO_API_URL = "http://lenovo:8088"  # Agent-ops API

class ChatMessage(BaseModel):
    message: str = Field(min_length=1)
    workspace: str | None = Field(default="/tmp/workspace")
    stream: bool = Field(default=True)

class TaskStatus(BaseModel):
    task_id: str
    status: str
    created_at: str
    result: dict | None = None
    error: str | None = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "hp-omen-orchestrator",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/chat")
async def chat_endpoint(msg: ChatMessage):
    """
    Main chat endpoint - creates task and returns streaming response
    """
    if msg.stream:
        return StreamingResponse(
            stream_chat_response(msg),
            media_type="text/event-stream"
        )
    else:
        # Non-streaming mode
        task_id = await create_task(msg.message, msg.workspace)
        return {"task_id": task_id, "status": "queued"}

async def stream_chat_response(msg: ChatMessage) -> AsyncGenerator[str, None]:
    """
    Stream chat response using Server-Sent Events (SSE)
    """
    try:
        # Create task on Lenovo
        task_id = await create_task(msg.message, msg.workspace)
        
        yield f"data: {json.dumps({'type': 'task_created', 'task_id': task_id})}\n\n"
        
        # Poll for status updates
        max_attempts = 60  # 5 minutes max (5 second intervals)
        for attempt in range(max_attempts):
            await asyncio.sleep(5)
            
            status = await get_task_status(task_id)
            
            yield f"data: {json.dumps({'type': 'status_update', 'status': status.status})}\n\n"
            
            if status.status == "succeeded":
                yield f"data: {json.dumps({'type': 'result', 'result': status.result})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                break
            elif status.status == "failed":
                yield f"data: {json.dumps({'type': 'error', 'error': status.error})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                break
        else:
            # Timeout
            yield f"data: {json.dumps({'type': 'error', 'error': 'Task timeout'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
    except Exception as e:
        logger.error(f"Stream error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

async def create_task(prompt: str, workspace: str) -> str:
    """Create task on Lenovo agent-ops API"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LENOVO_API_URL}/v1/runs",
            json={"prompt": prompt, "workspace": workspace},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        return data["id"]

async def get_task_status(task_id: str) -> TaskStatus:
    """Get task status from Lenovo agent-ops API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{LENOVO_API_URL}/v1/runs/{task_id}",
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        return TaskStatus(
            task_id=data["id"],
            status=data["status"],
            created_at=data["created_utc"],
            result=data.get("result"),
            error=data.get("error")
        )

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task status (non-streaming)"""
    try:
        status = await get_task_status(task_id)
        return status
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
