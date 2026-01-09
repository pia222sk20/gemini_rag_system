import os
import shutil
from typing import List
from fastapi import FastAPI, HTTPException, APIRouter, UploadFile, File, Query
from pydantic import BaseModel
from app.ingest import ingest_documents, DOC_DIR, CACHE_FILE, FileHashCache
from app.graph import app_graph
import uvicorn

from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="RAG-PRG API", 
    version="1.0",
    description="RAG System API for document ingestion and chat."
)

router = APIRouter(prefix="/api/v1")

# --- Data Models ---
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

class IngestResponse(BaseModel):
    status: str
    count: int = 0
    ingested_files: List[str] = []
    deleted_files: List[str] = []
    message: str

class DocumentInfo(BaseModel):
    filename: str
    size: int
    synced: bool

class DeleteDocumentsRequest(BaseModel):
    filenames: List[str]

# --- Endpoints ---

@router.get("/documents", response_model=List[DocumentInfo], tags=["Documents"])
async def list_documents():
    """
    **문서 목록 조회**
    
    DOC 폴더에 있는 모든 파일의 목록과 동기화 상태를 반환합니다.
    """
    if not os.path.exists(DOC_DIR):
        return []
    
    files = []
    cache = FileHashCache(CACHE_FILE)
    
    for filename in os.listdir(DOC_DIR):
        filepath = os.path.join(DOC_DIR, filename)
        if os.path.isfile(filepath) and not filename.startswith("."):
            is_synced = not cache.is_modified(filepath)
            files.append(DocumentInfo(
                filename=filename,
                size=os.path.getsize(filepath),
                synced=is_synced
            ))
    return files

@router.post("/documents", response_model=IngestResponse, tags=["Documents"])
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    **문서 업로드**
    
    하나 이상의 파일을 DOC 폴더에 업로드하고 자동으로 적재(Ingest)를 트리거합니다.
    """
    if not os.path.exists(DOC_DIR):
        os.makedirs(DOC_DIR)
        
    for file in files:
        file_location = os.path.join(DOC_DIR, file.filename)
        try:
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename}: {str(e)}")
            
    # Trigger ingestion
    try:
        result = ingest_documents()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.delete("/documents", response_model=IngestResponse, tags=["Documents"])
async def delete_documents(request: DeleteDocumentsRequest):
    """
    **문서 삭제**
    
    지정된 파일들을 DOC 폴더에서 삭제하고 벡터 DB에서도 제거합니다.
    """
    if not os.path.exists(DOC_DIR):
         return {"status": "success", "message": "DOC directory does not exist, nothing to delete."}

    deleted_count = 0
    errors = []

    for filename in request.filenames:
        filepath = os.path.join(DOC_DIR, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                deleted_count += 1
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
        else:
            errors.append(f"{filename}: File not found")

    # Trigger ingestion to sync deletes
    try:
        result = ingest_documents()
        if errors:
             result["message"] += f" (Errors: {', '.join(errors)})"
        return result
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Sync failed after delete: {str(e)}")


@router.post("/documents/sync", response_model=IngestResponse, tags=["Documents"])
async def sync_documents():
    """
    **문서 동기화 (수동)**
    
    DOC 폴더의 현재 상태를 기반으로 벡터 DB를 강제로 동기화합니다.
    (수동으로 파일을 넣거나 뺐을 때 유용함)
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
        result = app_graph.invoke(inputs)
        return ChatResponse(answer=result["generation"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
