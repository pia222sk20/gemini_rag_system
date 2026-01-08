from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from app.ingest import ingest_documents
from app.graph import app_graph
import uvicorn

app = FastAPI(
    title="RAG-PRG API", 
    version="1.0",
    description="RAG System API for document ingestion and chat."
)

# API Router 설정
router = APIRouter(prefix="/api/v1")

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

class IngestResponse(BaseModel):
    status: str
    count: int = 0
    message: str

@router.post("/documents/ingest", response_model=IngestResponse, tags=["Documents"])
async def ingest_endpoint():
    """
    **문서 적재 (Ingestion)**
    
    `DOC` 폴더에 있는 문서들(PDF, DOCX, TXT)을 읽어 벡터 데이터베이스에 적재합니다.
    """
    try:
        result = ingest_documents()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/completions", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """
    **질문하기 (Chat)**
    
    RAG 파이프라인을 통해 문서 기반의 정확한 답변을 생성합니다.
    """
    try:
        inputs = {"question": request.question}
        # LangGraph 실행
        result = app_graph.invoke(inputs)
        return ChatResponse(answer=result["generation"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 라우터 등록
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
