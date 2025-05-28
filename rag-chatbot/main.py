import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.documents import Document
from pydantic import BaseModel


load_dotenv()

app = FastAPI()

# Khởi tạo RAG chain một lần khi start app
rag_chain = None

def initialize_rag_chain():
    """Khởi tạo RAG chain một lần khi startup"""
    global rag_chain
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=os.getenv("GOOGLE_API_KEY"))
        vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))
        
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="Bạn là một trợ lý AI chuyên nghiệp của StreamCart. Dựa trên thông tin sau: {context}\nCâu hỏi: {question}\nHãy trả lời ngắn gọn, lịch sự và chính xác. Kết thúc bằng câu hỏi: 'Bạn có cần thêm chi tiết không?'"
        )
        
        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )
        print("RAG chain đã được khởi tạo thành công")
    except Exception as e:
        print(f"Lỗi khi khởi tạo RAG chain: {e}")

@app.on_event("startup")
async def startup_event():
    """Chạy khi app startup"""
    initialize_rag_chain()

def get_jwt_token():
    try:
        login_url = os.getenv("LOGIN_URL")
        credentials = {
            "email": os.getenv("API_EMAIL"),
            "password": os.getenv("API_PASSWORD")
        }
        response = requests.post(login_url, json=credentials)
        response.raise_for_status()  
        return response.json().get("token")
    except requests.RequestException as e:
        print(f"Lỗi khi lấy JWT token: {e}")
        return None

#Lấy dữ liệu từ API .NET
def fetch_data_from_api():
    try:
        # Thử lấy từ API trước
        token = get_jwt_token()
        if token:
            api_url = os.getenv("API_URL").replace("/swagger/index.html", "/api/data")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Không thể lấy dữ liệu từ API: {e}")
    
    # Fallback: sử dụng dữ liệu mẫu
    try:
        import json
        with open("sample_data.json", "r", encoding="utf-8") as f:
            print("Sử dụng dữ liệu mẫu để test...")
            return json.load(f)
    except Exception as e:
        print(f"Lỗi khi đọc file mẫu: {e}")
        return []

#index data 
def index_data():
    try:
        data = fetch_data_from_api()
        if not data:
            print("Không có dữ liệu để index")
            return
            
        documents = [Document(page_content=str(item)) for item in data]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=os.getenv("GOOGLE_API_KEY"))
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory="./chroma_db")
        vectorstore.persist()
        print("Data indexed successfully.")
    except Exception as e:
        print(f"Lỗi khi index dữ liệu: {e}")

#Process question greeting
def handle_greeting(question) : 
    question = question.lower().strip()
    greetings = ["xin chào", "chào", "hello", "hi", "bạn khỏe không", "how are you", "Dear", "Thân gửi"]
    if any(greeting in question for greeting in greetings):
        return "Xin chào! Tôi là trợ lý AI của StreamCart, sẵn sàng hỗ trợ. Bạn cần giúp gì hôm nay?"
    return None

#Setup RAG Chain with prompt template
def setup_rag_chain():
    """Deprecated: Sử dụng initialize_rag_chain() thay thế"""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=os.getenv("GOOGLE_API_KEY"))
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="Bạn là một trợ lý AI chuyên nghiệp. Dựa trên thông tin sau: {context}\nCâu hỏi: {question}\nHãy trả lời ngắn gọn, lịch sự và chính xác. Kết thúc bằng câu hỏi: 'Bạn có cần thêm chi tiết không?'"
    )
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )
    return rag_chain
# API endpoint để trả lời câu hỏi
class Query(BaseModel):
    question: str

@app.post("/api/chat")
async def chat(query: Query):
    try:
        # Kiểm tra câu hỏi chào hỏi
        greeting_response = handle_greeting(query.question)
        if greeting_response:
            return {"answer": greeting_response, "sources": []}
        
        # Kiểm tra RAG chain đã được khởi tạo chưa
        if not rag_chain:
            return {"error": "Hệ thống chưa sẵn sàng. Vui lòng thử lại sau."}, 500
        
        # Xử lý câu hỏi thông thường với RAG
        result = rag_chain({"query": query.question})
        return {
            "answer": result["result"], 
            "sources": [str(doc.page_content)[:200] + "..." for doc in result["source_documents"]]
        }
    except Exception as e:
        return {"error": f"Có lỗi xảy ra: {str(e)}"}, 500

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "rag_chain_ready": rag_chain is not None
    }

@app.post("/api/index")
async def trigger_indexing():
    """Endpoint để kích hoạt việc index dữ liệu"""
    try:
        index_data()
        initialize_rag_chain()
        return {"message": "Indexing completed successfully"}
    except Exception as e:
        return {"error": f"Indexing failed: {str(e)}"}, 500

if __name__ == "__main__":
    import uvicorn
    print("Bắt đầu indexing dữ liệu...")
    index_data()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)