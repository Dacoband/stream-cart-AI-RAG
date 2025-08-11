#!/usr/bin/env python3
"""
Webhook Integration Example
Minh họa cách AI Service sync chat history với Backend C# API
"""

import requests
import json
import logging
from typing import Optional
import asyncio
import uuid
from datetime import datetime

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("Warning: httpx not available, using fallback to requests")

class BackendWebhookService:
    """Service để sync chat history với Backend C# qua webhook"""
    
    def __init__(self, backend_url: str, webhook_secret: str = None):
        self.backend_url = backend_url.rstrip('/')
        self.webhook_secret = webhook_secret
        self.logger = logging.getLogger(__name__)
        
    async def sync_chat_message(self, message_data: dict) -> bool:
        """
        Sync một chat message với Backend C# API
        
        Args:
            message_data: Dictionary chứa thông tin chat message
            
        Returns:
            bool: True nếu sync thành công
        """
        try:
            url = f"{self.backend_url}/api/chathistory/sync"
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "StreamCart-AI-Service/1.0"
            }
            
            # Thêm webhook secret nếu có
            if self.webhook_secret:
                headers["X-Webhook-Secret"] = self.webhook_secret
            
            if HTTPX_AVAILABLE:
                # Use httpx for async requests
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(url, json=message_data, headers=headers)
                    status_code = response.status_code
                    response_text = response.text
            else:
                # Fallback to requests (blocking)
                response = requests.post(url, json=message_data, headers=headers, timeout=10.0)
                status_code = response.status_code
                response_text = response.text
                
            if status_code == 200:
                self.logger.info(f"Successfully synced message {message_data.get('messageId')} to backend")
                return True
            else:
                self.logger.error(f"Failed to sync message. Status: {status_code}, Response: {response_text}")
                return False
                    
        except Exception as e:
            self.logger.error(f"Error syncing message to backend: {e}")
            return False
    
    async def sync_session_update(self, session_data: dict) -> bool:
        """
        Sync session update với Backend
        
        Args:
            session_data: Dictionary chứa thông tin session
            
        Returns:
            bool: True nếu sync thành công
        """
        try:
            url = f"{self.backend_url}/api/chathistory/session-update"
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "StreamCart-AI-Service/1.0"
            }
            
            if self.webhook_secret:
                headers["X-Webhook-Secret"] = self.webhook_secret
            
            if HTTPX_AVAILABLE:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(url, json=session_data, headers=headers)
                    status_code = response.status_code
            else:
                response = requests.post(url, json=session_data, headers=headers, timeout=10.0)
                status_code = response.status_code
                
            if status_code == 200:
                self.logger.info(f"Successfully synced session {session_data.get('sessionId')} to backend")
                return True
            else:
                self.logger.error(f"Failed to sync session. Status: {status_code}")
                return False
                    
        except Exception as e:
            self.logger.error(f"Error syncing session to backend: {e}")
            return False

class ChatMessageProcessor:
    """Enhanced ChatbotService với Backend sync"""
    
    def __init__(self):
        self.webhook_service = BackendWebhookService(
            backend_url="https://api.streamcart.com",  # Backend C# API URL
            webhook_secret="your_webhook_secret_here"
        )
    
    async def process_and_sync_message(self, message: str, user_id: str, session_id: str) -> dict:
        """
        Xử lý message và sync với backend
        
        Args:
            message: User message
            user_id: User ID
            session_id: Session ID
            
        Returns:
            dict: Response data
        """
        try:
            # 1. Process message với AI (existing logic)
            ai_response = await self.process_with_ai(message, user_id, session_id)
            
            # 2. Tạo message data để sync
            message_data = {
                "messageId": str(uuid.uuid4()),
                "userId": user_id,
                "sessionId": session_id,
                "userMessage": message,
                "aiResponse": ai_response,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "metadata": {
                    "aiModel": "gemini-1.5-flash",
                    "responseTime": 1.2,  # Thời gian xử lý
                    "confidence": 0.95,   # Độ tin cậy
                    "source": "ai-service",
                    "version": "1.0.0"
                }
            }
            
            # 3. Sync với backend (async, không block response)
            asyncio.create_task(self.webhook_service.sync_chat_message(message_data))
            
            # 4. Trả response cho frontend
            return {
                "response": ai_response,
                "status": "success",
                "user_id": user_id,
                "session_id": session_id,
                "message_id": message_data["messageId"]
            }
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return {
                "response": "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.",
                "status": "error",
                "error": str(e)
            }
    
    async def process_with_ai(self, message: str, user_id: str, session_id: str) -> str:
        """
        Existing AI processing logic
        """
        # Placeholder for existing AI logic
        return f"AI response to: {message}"

# Example usage trong main.py
"""
# Trong main.py, thay đổi chat endpoint:

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, http_request: Request):
    try:
        # Get user info from headers
        user_id, session_id = user_session_manager.get_or_create_session(
            dict(http_request.headers)
        )
        
        # Process message với sync backend
        processor = ChatMessageProcessor()
        result = await processor.process_and_sync_message(
            request.message, 
            user_id, 
            session_id
        )
        
        # Save to local session (existing logic)
        user_session_manager.save_message(
            session_id, 
            request.message, 
            result["response"]
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
"""

# Retry mechanism cho webhook
class WebhookRetryService:
    """Service với retry mechanism cho webhook calls"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
    
    async def send_with_retry(self, webhook_service: BackendWebhookService, message_data: dict) -> bool:
        """
        Gửi webhook với retry mechanism
        """
        for attempt in range(self.max_retries):
            try:
                success = await webhook_service.sync_chat_message(message_data)
                if success:
                    return True
                    
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    
            except Exception as e:
                self.logger.warning(f"Webhook attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        self.logger.error(f"All {self.max_retries} webhook attempts failed for message {message_data.get('messageId')}")
        return False

# Queue-based sync cho high volume
import asyncio
from asyncio import Queue

class WebhookQueueService:
    """Service với queue để handle high volume webhook calls"""
    
    def __init__(self, webhook_service: BackendWebhookService, max_workers: int = 5):
        self.webhook_service = webhook_service
        self.queue = Queue()
        self.max_workers = max_workers
        self.running = False
        self.workers = []
        
    async def start(self):
        """Start queue workers"""
        self.running = True
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]
        
    async def stop(self):
        """Stop queue workers"""
        self.running = False
        
        # Wait for queue to be empty
        await self.queue.join()
        
        # Cancel workers
        for worker in self.workers:
            worker.cancel()
            
        await asyncio.gather(*self.workers, return_exceptions=True)
    
    async def enqueue_message(self, message_data: dict):
        """Add message to sync queue"""
        await self.queue.put(message_data)
    
    async def _worker(self, name: str):
        """Queue worker"""
        logger = logging.getLogger(f"webhook-{name}")
        
        while self.running:
            try:
                # Get message from queue with timeout
                message_data = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                # Try to sync
                retry_service = WebhookRetryService()
                success = await retry_service.send_with_retry(self.webhook_service, message_data)
                
                if success:
                    logger.info(f"Successfully processed message {message_data.get('messageId')}")
                else:
                    logger.error(f"Failed to sync message {message_data.get('messageId')} after all retries")
                
                # Mark task as done
                self.queue.task_done()
                
            except asyncio.TimeoutError:
                # No message in queue, continue
                continue
            except Exception as e:
                logger.error(f"Worker {name} error: {e}")
                
if __name__ == "__main__":
    # Demo webhook integration
    async def demo_webhook():
        webhook_service = BackendWebhookService(
            backend_url="https://api.streamcart.com",
            webhook_secret="demo_secret"
        )
        
        # Example message data
        message_data = {
            "messageId": "msg_123",
            "userId": "user_456",
            "sessionId": "session_789",
            "userMessage": "Hello AI!",
            "aiResponse": "Hello! How can I help you?",
            "timestamp": "2024-01-01T10:00:00Z",
            "metadata": {
                "aiModel": "gemini-1.5-flash",
                "responseTime": 1.5,
                "confidence": 0.98
            }
        }
        
        # Test sync
        success = await webhook_service.sync_chat_message(message_data)
        print(f"Webhook sync result: {success}")
    
    # Run demo
    asyncio.run(demo_webhook())
