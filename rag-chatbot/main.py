from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import logging
import time
import uuid

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="StreamCart AI Chatbot",
    description="AI Chatbot with Gemini Pro integration for product and shop information",
    version="1.0.0"
)

# Initialize Gemini model
gemini_api_key = os.getenv("GOOGLE_API_KEY")
backend_api_url = os.getenv("BACKEND_API_URL")

if not gemini_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Configure Gemini
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None      # Backend C# sẽ gửi user_id
    # Bỏ session_id - AI service sẽ tự tạo từ user_id

class ChatResponse(BaseModel):
    response: str
    status: str
    user_id: Optional[str] = None      # Trả về user_id
    error: Optional[str] = None
class UserSession:
    """Class để quản lý user session ở backend"""
    
    def __init__(self):
        self.sessions = {}  # Simple in-memory storage
        
    def get_or_create_session(self, request_headers: dict) -> tuple:
        """Lấy hoặc tạo session mới từ headers"""
        # Mô phỏng lấy user_id từ authentication header
        auth_header = request_headers.get("authorization", "")
        user_id = self.extract_user_id_from_auth(auth_header)
        
        # Tạo session_id mới
        import uuid
        session_id = str(uuid.uuid4())
        
        # Lưu session (có thể lưu vào database thực tế)
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": time.time(),
            "messages": []
        }
        
        return user_id, session_id
    
    def extract_user_id_from_auth(self, auth_header: str) -> str:
        """Trích xuất user_id từ authentication header"""
        if auth_header:
            # Mô phỏng decode JWT token hoặc API key
            if auth_header.startswith("Bearer "):
                # Ví dụ đơn giản - thực tế sẽ decode JWT
                token = auth_header.replace("Bearer ", "")
                if token == "demo_token_123":
                    return "user_authenticated_123"
                elif token == "demo_token_456":
                    return "user_authenticated_456"
        
        # Nếu không có auth, tạo anonymous user
        import uuid
        return f"anonymous_{str(uuid.uuid4())[:8]}"
    
    def save_message(self, session_id: str, message: str, response: str):
        """Lưu tin nhắn vào session"""
        if session_id in self.sessions:
            self.sessions[session_id]["messages"].append({
                "user_message": message,
                "ai_response": response,
                "timestamp": time.time()
            })

class APIService:
    """Service to handle external API calls"""
    
    @staticmethod
    def get_products() -> List[Dict]:
        """Fetch products from backend API"""
        try:
            response = requests.get(f"{backend_api_url}/api/products", timeout=10)
            response.raise_for_status()
            data = response.json()
            # API trả về format: {"success": true, "data": [...]}
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected products response format: {type(data)}")
                return []
        except requests.RequestException as e:
            logger.error(f"Error fetching products: {e}")
            return []
    
    @staticmethod
    def get_shops() -> List[Dict]:
        """Fetch shops from backend API"""
        try:
            response = requests.get(f"{backend_api_url}/api/shops", timeout=10)
            response.raise_for_status()
            data = response.json()
            # API trả về format: {"items": [...], "totalCount": 5}
            if isinstance(data, dict) and "items" in data:
                return data["items"]
            elif isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected shops response format: {type(data)}")
                return []
        except requests.RequestException as e:
            logger.error(f"Error fetching shops: {e}")
            return []
    
    @staticmethod
    def get_shop_by_id(shop_id: str) -> Dict:
        """Fetch specific shop by ID"""
        try:
            response = requests.get(f"{backend_api_url}/api/shops/{shop_id}", timeout=10)
            response.raise_for_status()
            data = response.json()
            # API trả về format: {"success": true, "data": {...}}
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, dict):
                return data
            else:
                logger.warning(f"Unexpected shop response format: {type(data)}")
                return {}
        except requests.RequestException as e:
            logger.error(f"Error fetching shop {shop_id}: {e}")
            return {}

class PromptTemplateService:
    """Custom prompt template service (替代 LangChain)"""
    
    @staticmethod
    def create_main_prompt(user_message: str, products_info: str, shops_info: str, context: str = "") -> str:
        """Create main chatbot prompt"""
        return f"""
Bạn là một trợ lý AI thông minh cho StreamCart - một nền tảng thương mại điện tử.
Bạn có khả năng trả lời câu hỏi về sản phẩm và cửa hàng dựa trên thông tin có sẵn.

THÔNG TIN SẢN PHẨM HIỆN TẠI:
{products_info}

THÔNG TIN CỬA HÀNG HIỆN TẠI:
{shops_info}

NGỮ CẢNH CUỘC TRỘI CHUYỆN:
{context}

CÂUHỎI CỦA NGƯỜI DÙNG: {user_message}

Hãy trả lời một cách tự nhiên, hữu ích và chính xác. Nếu thông tin không đủ để trả lời, hãy nói rõ và đề xuất cách khác để giúp đỡ.
Trả lời bằng tiếng Việt một cách thân thiện và chuyên nghiệp.

Lưu ý:
- Nếu người dùng hỏi về sản phẩm, hãy cung cấp thông tin chi tiết về sản phẩm phù hợp
- Nếu người dùng hỏi về cửa hàng, hãy cung cấp thông tin về các cửa hàng
- Nếu không có thông tin liên quan, hãy trả lời lịch sự và hướng dẫn người dùng
"""

    @staticmethod  
    def create_product_search_prompt(user_query: str, products: List[Dict]) -> str:
        """Create product search specific prompt"""
        products_text = json.dumps(products, ensure_ascii=False, indent=2)
        return f"""
Dựa trên danh sách sản phẩm sau và yêu cầu của người dùng, hãy tìm và giới thiệu các sản phẩm phù hợp:

DANH SÁCH SẢN PHẨM:
{products_text}

YÊU CẦU TÌM KIẾM: {user_query}

Hãy trả lời bằng tiếng Việt, giới thiệu các sản phẩm phù hợp với yêu cầu và cung cấp thông tin chi tiết về giá, mô tả, v.v.
"""

class ChatbotService:
    """Main chatbot service using Gemini"""
    
    def __init__(self):
        self.api_service = APIService()
        self.prompt_service = PromptTemplateService()
    
    def get_relevant_context(self, user_message: str) -> Dict[str, Any]:
        """Get relevant products and shops data based on user message"""
        context = {
            "products": [],
            "shops": [],
            "products_info": "Chưa có thông tin sản phẩm.",
            "shops_info": "Chưa có thông tin cửa hàng."
        }
        
        # Check if user is asking about products
        product_keywords = ["sản phẩm", "mua", "giá", "product", "price", "tìm kiếm", "tìm", "search"]
        if any(keyword in user_message.lower() for keyword in product_keywords):
            products = self.api_service.get_products()
            if products and isinstance(products, list):
                context["products"] = products
                context["products_info"] = self.format_products_info(products)
        
        # Check if user is asking about shops
        shop_keywords = ["cửa hàng", "shop", "store", "bán hàng", "địa chỉ"]
        if any(keyword in user_message.lower() for keyword in shop_keywords):
            shops = self.api_service.get_shops()
            if shops and isinstance(shops, list):
                context["shops"] = shops
                context["shops_info"] = self.format_shops_info(shops)
        
        return context
    
    def format_products_info(self, products: List[Dict]) -> str:
        """Format products information for prompt"""
        if not products:
            return "Không có sản phẩm nào."
        
        formatted = "DANH SÁCH SẢN PHẨM:\n"
        # Limit to first 5 products
        limited_products = products[:5] if len(products) > 5 else products
        
        for i, product in enumerate(limited_products, 1):
            name = product.get('productName', product.get('name', 'N/A'))
            price = product.get('finalPrice', product.get('basePrice', product.get('price', 'N/A')))
            description = product.get('description', 'N/A')
            product_id = product.get('id', 'N/A')
            
            formatted += f"{i}. Tên: {name}\n"
            formatted += f"   Giá: {price}\n"
            formatted += f"   Mô tả: {description}\n"
            formatted += f"   ID: {product_id}\n\n"
        
        return formatted
    
    def format_shops_info(self, shops: List[Dict]) -> str:
        """Format shops information for prompt"""
        if not shops:
            return "Không có cửa hàng nào."
        
        formatted = "DANH SÁCH CỬA HÀNG:\n"
        # Limit to first 5 shops
        limited_shops = shops[:5] if len(shops) > 5 else shops
        
        for i, shop in enumerate(limited_shops, 1):
            name = shop.get('shopName', shop.get('name', 'N/A'))
            description = shop.get('description', 'N/A')
            status = shop.get('status', 'N/A')
            approval_status = shop.get('approvalStatus', 'N/A')
            shop_id = shop.get('id', 'N/A')
            
            formatted += f"{i}. Tên: {name}\n"
            formatted += f"   Mô tả: {description}\n"
            formatted += f"   Trạng thái: {status}\n"
            formatted += f"   Phê duyệt: {approval_status}\n"
            formatted += f"   ID: {shop_id}\n\n"
        
        return formatted
    
    async def process_message(self, message: str, user_id: str = None, session_id: str = None, context: str = "") -> str:
        """Process user message and generate response using Gemini"""
        try:
            # Get relevant context from APIs
            api_context = self.get_relevant_context(message)
            
            # Add user and session info to context if provided
            enhanced_context = context
            if user_id or session_id:
                enhanced_context += f"\n[Thông tin phiên: User ID: {user_id or 'N/A'}, Session ID: {session_id or 'N/A'}]"
            
            # Create prompt using template service
            prompt = self.prompt_service.create_main_prompt(
                user_message=message,
                products_info=api_context["products_info"],
                shops_info=api_context["shops_info"],
                context=enhanced_context
            )
            
            # Send to Gemini
            response = model.generate_content(prompt)
            
            # Log the interaction (for future features)
            logger.info(f"Chat processed - User: {user_id}, Session: {session_id}, Message: {message[:50]}...")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

# Initialize chatbot service and user session manager
chatbot_service = ChatbotService()
user_session_manager = UserSession()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "StreamCart AI Chatbot API",
        "version": "1.0.0",
        "status": "active"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, http_request: Request):
    """Main chat endpoint - Simplified với chỉ user_id"""
    try:
        # Ưu tiên dùng user_id từ Backend C# request
        if request.user_id:
            # Called from Backend C# - dùng user_id được cung cấp
            user_id = request.user_id
            # Tạo session_id cố định cho user này: user_id chính là session
            session_id = f"user_{user_id}_main"
            logger.info(f"Processing chat from Backend C# - User: {user_id}")
        else:
            # Direct call hoặc legacy - tự tạo user_id từ headers
            user_id, session_id = user_session_manager.get_or_create_session(
                dict(http_request.headers)
            )
            logger.info(f"Processing direct chat - User: {user_id}")
        
        # Xử lý tin nhắn
        response = await chatbot_service.process_message(
            message=request.message,
            user_id=user_id,
            session_id=session_id,
            context=""
        )
        
        # Lưu tin nhắn vào session
        user_session_manager.save_message(session_id, request.message, response)
        
        return ChatResponse(
            response=response,
            status="success",
            user_id=user_id      # Trả về user_id (không cần session_id)
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        return ChatResponse(
            response="Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu của bạn.",
            status="error",
            error=str(e)
        )

@app.get("/products")
async def get_products():
    """Get all products from backend API"""
    try:
        products = chatbot_service.api_service.get_products()
        return {"products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/shops")
async def get_shops():
    """Get all shops from backend API"""
    try:
        shops = chatbot_service.api_service.get_shops()
        return {"shops": shops, "count": len(shops)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/shops/{shop_id}")
async def get_shop_by_id(shop_id: str):
    """Get specific shop by ID"""
    try:
        shop = chatbot_service.api_service.get_shop_by_id(shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop not found")
        return shop
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """Lấy lịch sử chat của session"""
    try:
        if session_id in user_session_manager.sessions:
            session_data = user_session_manager.sessions[session_id]
            return {
                "session_id": session_id,
                "user_id": session_data["user_id"],
                "created_at": session_data["created_at"],
                "message_count": len(session_data["messages"]),
                "messages": session_data["messages"]
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/history")
async def get_user_chat_history(user_id: str, page: int = 1, pageSize: int = 20):
    """Lấy lịch sử chat của user - Simplified"""
    try:
        # Tìm session chính của user (format: user_{user_id}_main)
        session_id = f"user_{user_id}_main"
        
        if session_id in user_session_manager.sessions:
            session_data = user_session_manager.sessions[session_id]
            messages = session_data["messages"]
            
            # Pagination
            total_messages = len(messages)
            start_idx = (page - 1) * pageSize
            end_idx = start_idx + pageSize
            paginated_messages = messages[start_idx:end_idx]
            
            return {
                "user_id": user_id,
                "total_messages": total_messages,
                "page": page,
                "page_size": pageSize,
                "total_pages": (total_messages + pageSize - 1) // pageSize,
                "messages": paginated_messages
            }
        else:
            return {
                "user_id": user_id,
                "total_messages": 0,
                "page": page,
                "page_size": pageSize,
                "total_pages": 0,
                "messages": []
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/user/{user_id}/history")
async def clear_user_chat_history(user_id: str):
    """Xóa lịch sử chat của user"""
    try:
        session_id = f"user_{user_id}_main"
        
        if session_id in user_session_manager.sessions:
            # Xóa session
            del user_session_manager.sessions[session_id]
            return {
                "message": f"Chat history cleared for user {user_id}",
                "user_id": user_id
            }
        else:
            return {
                "message": f"No chat history found for user {user_id}",
                "user_id": user_id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/sessions")
async def get_user_sessions(user_id: str):
    """Lấy tất cả sessions của một user"""
    try:
        user_sessions = []
        for session_id, session_data in user_session_manager.sessions.items():
            if session_data["user_id"] == user_id:
                user_sessions.append({
                    "session_id": session_id,
                    "created_at": session_data["created_at"],
                    "message_count": len(session_data["messages"])
                })
        
        return {
            "user_id": user_id,
            "total_sessions": len(user_sessions),
            "sessions": user_sessions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "gemini_configured": bool(gemini_api_key),
        "backend_api_url": backend_api_url,
        "active_sessions": len(user_session_manager.sessions)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
