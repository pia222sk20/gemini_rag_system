import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# 환경 변수에서 설정 로드 (Docker 환경 고려)
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
COLLECTION_NAME = "rag_graph"

def get_vectorstore():
    """
    ChromaDB 벡터 스토어 인스턴스를 반환합니다.
    """
    embeddings = OpenAIEmbeddings()
    
    # HttpClient를 사용하여 Docker 컨테이너의 ChromaDB에 접속
    # 로컬 개발 시에는 persistent_client를 사용하거나 설정에 따라 분기 가능
    # 여기서는 Docker 환경을 기본으로 HttpClient 사용
    import chromadb
    client = chromadb.HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))
    
    vectorstore = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )
    return vectorstore

def get_retriever():
    """
    검색기(Retriever)를 반환합니다.
    """
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever()
