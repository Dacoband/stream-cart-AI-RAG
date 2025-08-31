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
import difflib
import re

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

# System guardrails để AI chỉ trả lời trong phạm vi StreamCart
SYSTEM_INSTRUCTIONS = (
    "Bạn chỉ là trợ lý dành riêng cho nền tảng thương mại điện tử StreamCart. "
    "Chỉ trả lời câu hỏi liên quan tới: sản phẩm, cửa hàng, mua sắm, giá, trạng thái cửa hàng, quy trình mua hàng, hỗ trợ người dùng trên StreamCart. "
    "KHÔNG trả lời các chủ đề ngoài phạm vi (ví dụ: chính trị, thời tiết, tin tức thời sự, y tế, tài chính cá nhân, lập trình, tiền mã hoá, chuyện đời tư, nội dung nhạy cảm). "
    "Khi câu hỏi nằm ngoài phạm vi, hãy lịch sự từ chối và hướng người dùng quay lại các chủ đề về sản phẩm / cửa hàng trên StreamCart. "
    "Không suy đoán hoặc bịa thông tin. Nếu dữ liệu không có, hãy nói rõ và mời người dùng cung cấp thêm chi tiết. "
    "Không tiết lộ ID nội bộ, token, thông tin nhạy cảm kỹ thuật. "
    "Trả lời ngắn gọn, rõ ràng, bằng tiếng Việt, thân thiện, chuyên nghiệp."
)

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
    # Simple in-memory cache: key -> (timestamp, data)
    _cache: Dict[str, tuple] = {}
    _CACHE_TTL_SECONDS = 60

    @classmethod
    def _cache_key(cls, name: str, **params) -> str:
        return name + "|" + "&".join(f"{k}={v}" for k, v in sorted(params.items()))

    @classmethod
    def _cache_get(cls, key: str):
        item = cls._cache.get(key)
        if not item:
            return None
        ts, data = item
        if time.time() - ts > cls._CACHE_TTL_SECONDS:
            # expired
            cls._cache.pop(key, None)
            return None
        return data

    @classmethod
    def _cache_set(cls, key: str, data):
        cls._cache[key] = (time.time(), data)

    @staticmethod
    def get_current_flash_sales() -> List[Dict]:
        """Fetch current flash sales from backend API"""
        try:
            url = f"{backend_api_url}/api/flashsales/current"
            cache_key = APIService._cache_key("get_current_flash_sales")
            cached = APIService._cache_get(cache_key)
            if cached is not None:
                return cached
            logger.info(f"Fetching current flash sales: GET {url}")
            response = requests.get(url, timeout=10)
            logger.info(f"Flash sales response status={response.status_code}")
            response.raise_for_status()
            raw_text = response.text
            try:
                data = response.json()
            except ValueError:
                logger.error(f"Flash sales response not JSON: {raw_text[:300]}")
                return []
            # Expected format: {"success": true, "data": [...]} but fallback to list
            flash_list: List[Dict] = []
            if isinstance(data, dict):
                if isinstance(data.get("data"), list):
                    flash_list = data["data"]
                elif isinstance(data.get("items"), list):
                    flash_list = data["items"]
                elif isinstance(data.get("result"), list):
                    flash_list = data["result"]
                elif isinstance(data.get("Results"), list):
                    flash_list = data["Results"]
                else:
                    # maybe the dict itself is a single flash sale object
                    if {"productName", "flashSalePrice"}.issubset(set(data.keys())):
                        flash_list = [data]
            elif isinstance(data, list):
                flash_list = data
            APIService._cache_set(cache_key, flash_list)
            return flash_list
        except requests.RequestException as e:
            logger.error(f"Error fetching current flash sales: {e}")
            return []
    
    @staticmethod
    def get_products() -> List[Dict]:
        """Fetch products from backend API"""
        try:
            cache_key = APIService._cache_key("get_products")
            cached = APIService._cache_get(cache_key)
            if cached is not None:
                return cached
            response = requests.get(f"{backend_api_url}/api/products", timeout=10)
            response.raise_for_status()
            data = response.json()
            # API trả về format: {"success": true, "data": [...]}
            if isinstance(data, dict) and "data" in data:
                APIService._cache_set(cache_key, data["data"])
                return data["data"]
            elif isinstance(data, list):
                APIService._cache_set(cache_key, data)
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
            url = f"{backend_api_url}/api/shops"
            params = {"pageNumber": 1, "pageSize": 10, "ascending": "true"}
            cache_key = APIService._cache_key("get_shops", **params)
            cached = APIService._cache_get(cache_key)
            if cached is not None:
                return cached
            logger.info(f"Fetching shops: GET {url} params={params}")
            response = requests.get(url, params=params, timeout=10)
            logger.info(f"Shops response status={response.status_code}")
            response.raise_for_status()
            raw_text = response.text
            try:
                data = response.json()
            except ValueError:
                logger.error(f"Shops response is not JSON: {raw_text[:300]}")
                return []
            # API trả về format: {"items": [...], "totalCount": 5} hoặc {"data": [...]}
            shops_list: List[Dict] = []
            if isinstance(data, dict):
                if "items" in data and isinstance(data["items"], list):
                    shops_list = data["items"]
                elif "data" in data and isinstance(data["data"], list):
                    shops_list = data["data"]
                else:
                    # Một số API có thể bọc trong key khác như "result" hoặc trả thẳng object phân trang
                    for key in ["result", "Results", "shops", "Shops"]:
                        if key in data and isinstance(data[key], list):
                            shops_list = data[key]
                            break
                    if not shops_list:
                        logger.warning(f"Unexpected shops response keys: {list(data.keys())}")
                        shops_list = []
            elif isinstance(data, list):
                shops_list = data
            else:
                logger.warning(f"Unexpected shops response type: {type(data)}")
                shops_list = []

            # Filter chỉ lấy shop đã phê duyệt (approvalStatus == 'Approved') và active nếu có field status
            before_count = len(shops_list)
            filtered = [s for s in shops_list if (str(s.get('approvalStatus', '')).lower() == 'approved'.lower()) and (s.get('status', True) in [True, 'true', 1])]
            logger.info(f"Shops filtering: before={before_count} after={len(filtered)} approved+active")
            APIService._cache_set(cache_key, filtered)
            return filtered
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

    @staticmethod
    def get_products_by_shop(shop_id: str, active_only: bool = True) -> List[Dict]:
        """Fetch products belonging to a specific shop"""
        try:
            url = f"{backend_api_url}/api/products/shop/{shop_id}"
            params = {"activeOnly": str(active_only).lower()}
            cache_key = APIService._cache_key("get_products_by_shop", shop_id=shop_id, activeOnly=params["activeOnly"])
            cached = APIService._cache_get(cache_key)
            if cached is not None:
                return cached
            logger.info(f"Fetching products of shop {shop_id}: GET {url} params={params}")
            response = requests.get(url, params=params, timeout=10)
            logger.info(f"Shop products response status={response.status_code}")
            response.raise_for_status()
            raw_text = response.text
            try:
                data = response.json()
            except ValueError:
                logger.error(f"Shop products response not JSON: {raw_text[:300]}")
                return []
            # Possible formats similar to other endpoints
            if isinstance(data, dict):
                for key in ["items", "data", "products", "Products", "result", "Results"]:
                    if key in data and isinstance(data[key], list):
                        APIService._cache_set(cache_key, data[key])
                        return data[key]
                # If dict itself is product object, wrap
                if all(k in data for k in ["productName", "name", "id"]):
                    APIService._cache_set(cache_key, [data])
                    return [data]
                logger.warning(f"Unexpected shop products keys: {list(data.keys())}")
                return []
            elif isinstance(data, list):
                APIService._cache_set(cache_key, data)
                return data
            else:
                logger.warning(f"Unexpected shop products response type: {type(data)}")
                return []
        except requests.RequestException as e:
            logger.error(f"Error fetching products for shop {shop_id}: {e}")
            return []

class PromptTemplateService:
    """Custom prompt template service (替代 LangChain)"""

    @staticmethod
    def create_main_prompt(user_message: str, products_info: str, shops_info: str, flash_sales_info: str = "", context: str = "") -> str:
        """Create main chatbot prompt"""
        return f"""
HƯỚNG DẪN HỆ THỐNG (KHÔNG TIẾT LỘ CHO NGƯỜI DÙNG):
{SYSTEM_INSTRUCTIONS}

THÔNG TIN SẢN PHẨM:
{products_info}

THÔNG TIN CỬA HÀNG:
{shops_info}

FLASH SALE HIỆN TẠI:
{flash_sales_info}

NGỮ CẢNH:
{context}

CÂU HỎI NGƯỜI DÙNG: {user_message}

YÊU CẦU TRẢ LỜI:
- Nếu câu hỏi ngoài phạm vi StreamCart: từ chối nhẹ nhàng, gợi ý hỏi về sản phẩm / cửa hàng.
- Nếu thiếu dữ liệu: nói rõ chưa có thông tin.
- Không đưa ID nội bộ hay thông số kỹ thuật.
- Ngắn gọn, chính xác, tiếng Việt.
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
        context: Dict[str, Any] = {
            "products": [],
            "shops": [],
            "products_info": "Chưa có thông tin sản phẩm.",
            "shops_info": "Chưa có thông tin cửa hàng.",
            "matched_shop": None,
            "flash_sales": [],
            "flash_sales_info": "Chưa có flash sale nào."
        }

        # --- Parse potential filters ---
        price_filter = self.parse_price_filter(user_message)
        status_filter = self.parse_status_filter(user_message)

        # --- Product intent detection ---
        product_keywords = ["sản phẩm", "mua", "giá", "product", "price", "tìm kiếm", "tìm", "search"]
        lower_msg = user_message.lower()
        if any(keyword in lower_msg for keyword in product_keywords):
            products = self.api_service.get_products()
            if products:
                products = self.apply_product_filters(products, price_filter, status_filter)
            if products:
                context["products"] = products
                context["products_info"] = self.format_products_info(products)

        # --- Shop intent detection (and possibly shop-specific products) ---
        shop_keywords = ["cửa hàng", "shop", "store", "bán hàng", "địa chỉ", "bán những gì", "bán gì"]
        if any(keyword in lower_msg for keyword in shop_keywords):
            shops = self.api_service.get_shops()
            if shops:
                context["shops"] = shops
                context["shops_info"] = self.format_shops_info(shops)
                matched = None
                for shop in shops:
                    shop_name = str(shop.get('shopName') or shop.get('name') or '').strip()
                    if shop_name and shop_name.lower() in lower_msg:
                        matched = shop
                        break
                if not matched:
                    possible_names = [str(s.get('shopName') or s.get('name') or '').strip() for s in shops]
                    possible_names = [n for n in possible_names if n]
                    best_name = None
                    best_ratio = 0.0
                    for name in possible_names:
                        ratio = difflib.SequenceMatcher(None, name.lower(), lower_msg).ratio()
                        if ratio > best_ratio:
                            best_ratio = ratio
                            best_name = name
                    if best_ratio >= 0.6 and best_name:
                        for s in shops:
                            if (s.get('shopName') or s.get('name')) == best_name:
                                matched = s
                                break
                if matched:
                    context["matched_shop"] = matched
                    shop_id = matched.get('id')
                    if shop_id:
                        shop_products = self.api_service.get_products_by_shop(shop_id)
                        if shop_products:
                            shop_products = self.apply_product_filters(shop_products, price_filter, status_filter)
                        if shop_products:
                            limited = shop_products[:10]
                            context["products"] = limited
                            context["products_info"] = (
                                "SẢN PHẨM CỦA CỬA HÀNG: "
                                + (matched.get('shopName') or matched.get('name') or '')
                                + "\n" + self.format_products_info(limited)
                            )
                        else:
                            context["products_info"] = (
                                "Chưa tìm thấy sản phẩm nào cho cửa hàng "
                                + (matched.get('shopName') or matched.get('name') or '')
                            )

        # --- Flash sale intent detection ---
        flash_keywords = [
            "flash sale", "flashsale", "flash-sales", "deal sốc", "giờ vàng", "sale sốc", "sale giờ vàng",
            "giảm giá nhanh", "chớp nhoáng", "deal hot", "deal hôm nay"
        ]
        if any(k in lower_msg for k in flash_keywords):
            flash_sales = self.api_service.get_current_flash_sales()
            if flash_sales:
                context["flash_sales"] = flash_sales
                context["flash_sales_info"] = self.format_flash_sales_info(flash_sales)
            else:
                context["flash_sales_info"] = "Hiện tại chưa có chương trình flash sale đang diễn ra."    

        return context

    # ---------------- Product filter helpers -----------------
    def parse_price_filter(self, message: str) -> Dict[str, Optional[float]]:
        """Detect price range in message. Supports patterns: 'dưới 100k', 'trên 200k', 'từ 100k đến 300k', '100k-300k'"""
        m = message.lower()
        # Normalize k -> *1000
        def to_number(token: str):
            token = token.strip().lower().replace('.', '').replace(',', '')
            mult = 1
            if token.endswith('k'):
                mult = 1000
                token = token[:-1]
            try:
                return float(token) * mult
            except ValueError:
                return None
        # range patterns
        range_patterns = [r"(\d+\s*k)\s*[-đếnto]{1,4}\s*(\d+\s*k)", r"từ\s*(\d+\s*k)\s*(?:đến|tới|-)\s*(\d+\s*k)"]
        for pat in range_patterns:
            r = re.search(pat, m)
            if r:
                v1 = to_number(r.group(1))
                v2 = to_number(r.group(2))
                if v1 and v2:
                    return {"min": min(v1, v2), "max": max(v1, v2)}
        # dưới / dưới hơn
        r = re.search(r"dưới\s*(\d+\s*k)", m)
        if r:
            v = to_number(r.group(1))
            if v:
                return {"min": None, "max": v}
        r = re.search(r"trên\s*(\d+\s*k)", m)
        if r:
            v = to_number(r.group(1))
            if v:
                return {"min": v, "max": None}
        return {"min": None, "max": None}

    def parse_status_filter(self, message: str) -> Optional[str]:
        m = message.lower()
        if "còn hàng" in m or "in stock" in m:
            return "in_stock"
        if "hết hàng" in m or "out of stock" in m:
            return "out_of_stock"
        if "đang giảm" in m or "sale" in m or "khuyến mãi" in m:
            return "on_sale"
        return None

    def apply_product_filters(self, products: List[Dict], price_filter: Dict[str, Optional[float]], status_filter: Optional[str]) -> List[Dict]:
        def price_of(p: Dict):
            for key in ["finalPrice", "basePrice", "price"]:
                if key in p and isinstance(p[key], (int, float)):
                    return p[key]
                # try str to float
                if key in p:
                    try:
                        return float(str(p[key]).replace(',', '').replace('.', ''))
                    except Exception:
                        continue
            return None
        filtered = []
        for p in products:
            price = price_of(p)
            if price_filter["min"] is not None and (price is None or price < price_filter["min"]):
                continue
            if price_filter["max"] is not None and (price is None or price > price_filter["max"]):
                continue
            if status_filter:
                status_val = str(p.get('status', p.get('isActive', p.get('inStock', '')))).lower()
                if status_filter == "in_stock" and status_val in ["false", "0", "out", "hết", "inactive"]:
                    continue
                if status_filter == "out_of_stock" and status_val in ["true", "1", "active", "còn"]:
                    continue
                if status_filter == "on_sale":
                    # heuristic: compare basePrice vs finalPrice
                    base = p.get('basePrice') or p.get('price')
                    final = p.get('finalPrice') or base
                    try:
                        if final is None or base is None or float(final) >= float(base):
                            continue
                    except Exception:
                        continue
            filtered.append(p)
        return filtered or products  # fallback if filter removes all

    # ---------------- Knowledge base -----------------
    def get_additional_context(self, message: str) -> str:
        m = message.lower()
        snippets = []
        kb = [
            (['thanh toán', 'payment', 'trả tiền'], "Phương thức thanh toán: hỗ trợ ví điện tử, thẻ ngân hàng nội địa và quốc tế, COD tùy khu vực."),
            (['vận chuyển', 'giao hàng', 'ship'], "Vận chuyển: đối tác giao hàng tiêu chuẩn 2-5 ngày làm việc, có tuỳ chọn nhanh ở một số tỉnh."),
            (['đổi trả', 'hoàn hàng', 'trả hàng', 'refund'], "Đổi trả: chấp nhận trong 7 ngày nếu sản phẩm lỗi / sai mô tả, cần video & ảnh khi nhận hàng."),
            (['khuyến mãi', 'mã giảm', 'voucher', 'giảm giá'], "Khuyến mãi: nhập mã tại bước thanh toán; mỗi đơn áp dụng tối đa 1 mã + freeship nếu đủ điều kiện."),
            (['hỗ trợ', 'support', 'liên hệ', 'care'], "Hỗ trợ: bạn có thể gửi câu hỏi qua mục Trợ giúp hoặc chat trực tiếp trong khung giờ 8h-22h."),
            (['đơn hàng', 'tình trạng đơn', 'tracking', 'mã đơn'], "Theo dõi đơn: vào mục 'Đơn hàng của tôi' để xem trạng thái cập nhật thời gian thực."),
            (['flash sale', 'deal sốc', 'giờ vàng', 'sale giờ vàng', 'flashsale'], "Flash Sale: diễn ra trong khung giờ giới hạn, số lượng có hạn, nên thanh toán sớm để giữ mức giá ưu đãi.")
        ]
        for keys, text in kb:
            if any(k in m for k in keys):
                snippets.append(text)
        return "\n".join(snippets)
    
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
            
            formatted += f"{i}. Tên: {name}\n"
            formatted += f"   Giá: {price}\n"
            formatted += f"   Mô tả: {description}\n\n"
        
        return formatted

    def is_out_of_scope(self, message: str) -> bool:
        """Rất đơn giản: phát hiện một số chủ đề ngoài phạm vi để từ chối sớm."""
        oos_keywords = [
            "thời tiết", "weather", "chính trị", "politics", "bóng đá", "football",
            "crypto", "tiền ảo", "coin", "chứng khoán", "stock", "forex", "tiểu sử",
            "life story", "tiểu thuyết", "game", "anime", "phim", "movie"
        ]
        m_lower = message.lower()
        return any(k in m_lower for k in oos_keywords)
    
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
            
            formatted += f"{i}. Tên: {name}\n"
            formatted += f"   Mô tả: {description}\n"
            formatted += f"   Trạng thái: {status}\n"
            formatted += f"   Phê duyệt: {approval_status}\n\n"
        
        return formatted

    def format_flash_sales_info(self, flash_sales: List[Dict]) -> str:
        """Format flash sales information for prompt (hide internal IDs)"""
        if not flash_sales:
            return "Không có flash sale nào."
        formatted = "FLASH SALE ĐANG DIỄN RA:\n"
        limited = flash_sales[:5]
        for i, fs in enumerate(limited, 1):
            pname = fs.get('productName') or fs.get('name') or 'Sản phẩm'
            flash_price = fs.get('flashSalePrice')
            base_price = fs.get('price') or fs.get('originalPrice')
            discount = None
            try:
                if flash_price is not None and base_price not in [None, 0]:
                    discount = round(100 - (float(flash_price) / float(base_price) * 100))
            except Exception:
                discount = None
            qty_avail = fs.get('quantityAvailable')
            qty_sold = fs.get('quantitySold')
            slot = fs.get('slot')
            end_time = fs.get('endTime')
            formatted += f"{i}. {pname} - Giá flash: {flash_price} (Giá gốc: {base_price}" + (f", -{discount}%" if discount is not None else "") + ")\n"
            formatted += f"   Số lượng: còn {qty_avail} đã bán {qty_sold}; Slot: {slot}; Kết thúc: {end_time}\n"
        return formatted
    
    async def process_message(self, message: str, user_id: str = None, session_id: str = None, context: str = "") -> str:
        """Process user message and generate response using Gemini"""
        try:
            # Get relevant context from APIs
            api_context = self.get_relevant_context(message)

            # Out-of-scope quick check (câu trả lời quy chuẩn, không gọi model để tiết kiệm)
            if self.is_out_of_scope(message):
                return (
                    "Xin lỗi, tôi chỉ hỗ trợ các câu hỏi liên quan đến nền tảng StreamCart như sản phẩm, cửa hàng, giá, đặt hàng và hỗ trợ sử dụng. "
                    "Bạn có thể hỏi: 'Có những cửa hàng nào?', 'Giá sản phẩm A?', 'Cách mua hàng?'"
                )
            
            # Create prompt using template service (loại bỏ thông tin nhạy cảm)
            extra_context = self.get_additional_context(message)
            combined_products_info = api_context["products_info"]
            if extra_context:
                combined_products_info += "\n\nTHÔNG TIN THÊM:\n" + extra_context
            prompt = self.prompt_service.create_main_prompt(
                user_message=message,
                products_info=combined_products_info,
                shops_info=api_context["shops_info"],
                flash_sales_info=api_context.get("flash_sales_info", ""),
                context=""  # Không thêm context nhạy cảm
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
        if request.user_id:
            user_id = request.user_id
            session_id = f"user_{user_id}_main"
            logger.info(f"Processing chat from Backend C# - User: {user_id}")
        else:
            user_id, session_id = user_session_manager.get_or_create_session(
                dict(http_request.headers)
            )
            logger.info(f"Processing direct chat - User: {user_id}")
        response = await chatbot_service.process_message(
            message=request.message,
            user_id=user_id,
            session_id=session_id,
            context=""
        )
        user_session_manager.save_message(session_id, request.message, response)
        
        return ChatResponse(
            response=response,
            status="success",
            user_id=user_id
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

@app.get("/shops/{shop_id}/products")
async def get_products_by_shop(shop_id: str, activeOnly: bool = True):
    """Get products of a specific shop"""
    try:
        products = chatbot_service.api_service.get_products_by_shop(shop_id, active_only=activeOnly)
        return {"shop_id": shop_id, "count": len(products), "products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/flashsales/current")
async def get_current_flash_sales():
    """Get current flash sales"""
    try:
        flash_sales = chatbot_service.api_service.get_current_flash_sales()
        return {"count": len(flash_sales), "flash_sales": flash_sales}
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
