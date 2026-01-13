"""
Predator Helios Worker - AI Brain
WebSocket-based worker that communicates with HP OMEN orchestrator
Runs on Windows with Docker Desktop + WSL2
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeliosWorker:
    def __init__(self, omen_url: str = "ws://hp-omen:8080/ws"):
        self.omen_url = omen_url
        self.running = False
        
    async def connect(self):
        """Connect to HP OMEN orchestrator"""
        logger.info(f"Connecting to HP OMEN at {self.omen_url}")
        async with websockets.connect(self.omen_url) as websocket:
            self.running = True
            logger.info("Connected to HP OMEN orchestrator")
            
            # Send registration
            await websocket.send(json.dumps({
                "type": "register",
                "worker_id": "predator-helios",
                "capabilities": ["code", "terminal", "file_editor"],
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            # Main loop
            while self.running:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    await self.handle_message(json.loads(message), websocket)
                except asyncio.TimeoutError:
                    # Send heartbeat
                    await websocket.send(json.dumps({
                        "type": "heartbeat",
                        "worker_id": "predator-helios",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("Connection closed, reconnecting...")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    
    async def handle_message(self, message: dict, websocket):
        """Handle incoming messages from orchestrator"""
        msg_type = message.get("type")
        
        if msg_type == "task":
            await self.process_task(message, websocket)
        elif msg_type == "ping":
            await websocket.send(json.dumps({"type": "pong"}))
        else:
            logger.warning(f"Unknown message type: {msg_type}")
            
    async def process_task(self, task: dict, websocket):
        """Process task from orchestrator"""
        task_id = task.get("task_id")
        logger.info(f"Processing task {task_id}")
        
        try:
            # Send acknowledgment
            await websocket.send(json.dumps({
                "type": "task_ack",
                "task_id": task_id,
                "status": "processing"
            }))
            
            # Simulate work (in production, this calls OpenHands SDK)
            await asyncio.sleep(2)
            
            # Send result
            await websocket.send(json.dumps({
                "type": "task_result",
                "task_id": task_id,
                "status": "completed",
                "result": {
                    "summary": "Task completed successfully",
                    "artifacts": []
                }
            }))
            
        except Exception as e:
            logger.error(f"Task processing error: {e}")
            await websocket.send(json.dumps({
                "type": "task_error",
                "task_id": task_id,
                "error": str(e)
            }))
            
    async def run(self):
        """Main run loop with auto-reconnect"""
        while True:
            try:
                await self.connect()
            except Exception as e:
                logger.error(f"Connection error: {e}")
                logger.info("Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

if __name__ == "__main__":
    worker = HeliosWorker()
    asyncio.run(worker.run())
