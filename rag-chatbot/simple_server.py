import os
import json
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

# FastAPI app instance
app = FastAPI(title="StreamCart RAG Chatbot", version="1.0.0")

# Load sample data
def load_sample_data():
    try:
        with open("sample_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu mẫu: {e}")
        return []

# Sample data
sample_data = load_sample_data()

class Query(BaseModel):
    question: str

def handle_greeting(question: str) -> str:
    question = question.lower().strip()
    greetings = ["xin chào", "chào", "hello", "hi", "bạn khỏe không", "how are you"]
    if any(greeting in question for greeting in greetings):
        return "Xin chào! Tôi là trợ lý AI của StreamCart, sẵn sàng hỗ trợ. Bạn cần giúp gì hôm nay?"
    return None

def simple_search(question: str):
    """Tìm kiếm đơn giản trong dữ liệu mẫu"""
    question_lower = question.lower()
    results = []
    
    for item in sample_data:
        # Tìm kiếm trong title và description
        title = item.get("title", "").lower()
        description = item.get("description", "").lower()
        
        if question_lower in title or question_lower in description:
            results.append(item)
        elif any(word in title or word in description for word in question_lower.split()):
            results.append(item)
    
    return results

@app.get("/")
async def root():
    return {"message": "StreamCart RAG Chatbot API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "data_loaded": len(sample_data) > 0,
        "total_items": len(sample_data)
    }

@app.post("/api/chat")
async def chat(query: Query):
    try:
        # Kiểm tra câu hỏi chào hỏi
        greeting_response = handle_greeting(query.question)
        if greeting_response:
            return {"answer": greeting_response, "sources": []}
        
        # Tìm kiếm trong dữ liệu
        results = simple_search(query.question)
        
        if results:
            # Tạo response từ kết quả tìm kiếm
            answer = f"Tôi tìm thấy {len(results)} kết quả liên quan:\n\n"
            for i, item in enumerate(results[:3], 1):  # Giới hạn 3 kết quả
                answer += f"{i}. {item.get('title', 'N/A')}\n"
                answer += f"   {item.get('description', 'N/A')}\n\n"
            
            answer += "Bạn có cần thêm chi tiết không?"
            
            return {
                "answer": answer,
                "sources": [item.get('title', 'N/A') for item in results[:3]]
            }
        else:
            return {
                "answer": "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn. Bạn có thể hỏi về sản phẩm, dịch vụ, hoặc chính sách của StreamCart.",
                "sources": []
            }
    
    except Exception as e:
        return {"error": f"Có lỗi xảy ra: {str(e)}"}, 500

if __name__ == "__main__":
    print("Starting StreamCart RAG Chatbot...")
    print(f"Loaded {len(sample_data)} sample items")
    uvicorn.run(app, host="127.0.0.1", port=8000)
