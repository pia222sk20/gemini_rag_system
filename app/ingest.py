import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.vectorstore import get_vectorstore

DOC_DIR = os.path.join(os.getcwd(), "DOC")

def ingest_documents():
    """
    DOC 폴더의 문서(TXT, PDF, DOCX)를 읽어 벡터 스토어에 적재합니다.
    """
    if not os.path.exists(DOC_DIR):
        os.makedirs(DOC_DIR)
        print(f"Created directory: {DOC_DIR}")
        return {"status": "empty", "message": "DOC directory was empty and has been created."}

    docs = []
    
    # TXT 파일 로드
    txt_loader = DirectoryLoader(DOC_DIR, glob="**/*.txt", loader_cls=TextLoader)
    docs.extend(txt_loader.load())
    
    # PDF 파일 로드
    pdf_loader = DirectoryLoader(DOC_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader)
    docs.extend(pdf_loader.load())
    
    # DOCX 파일 로드
    docx_loader = DirectoryLoader(DOC_DIR, glob="**/*.docx", loader_cls=Docx2txtLoader)
    docs.extend(docx_loader.load())
    
    if not docs:
        return {"status": "empty", "message": "No documents (.txt, .pdf, .docx) found in DOC directory."}

    # 텍스트 분할 (청크 사이즈 조절 가능)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # 벡터 스토어에 저장
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents=splits)
    
    return {"status": "success", "count": len(splits), "message": f"Successfully ingested {len(splits)} chunks from {len(docs)} documents."}
