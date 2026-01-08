# RAG 시스템 가이드

## 시스템 개요
이 시스템은 FastAPI 기반의 RAG(Retrieval-Augmented Generation) 챗봇 백엔드입니다. LangGraph를 사용하여 에이전트 워크플로우를 제어하고, ChromaDB를 벡터 저장소로 사용합니다.

## 로컬 실행 방법 (Docker)
1.  **사전 준비:** `docker-desktop` 실행, `.env` 파일에 `OPENAI_API_KEY` 설정.
2.  **실행:**
    ```bash
    docker-compose up --build
    ```
3.  **API 확인:** `http://localhost:8080/docs`

## 배포 방법 (Render.com)
이 프로젝트는 Render.com의 **Docker Runtime**을 통해 무료로 배포할 수 있습니다.

1.  GitHub 저장소(`https://github.com/pia222sk20/gemini_rag_system.git`)를 Render에 연결합니다.
2.  **Web Service**를 생성하고 Runtime을 **Docker**로 설정합니다.
3.  **Environment Variables**에 `OPENAI_API_KEY`를 추가합니다.
4.  배포가 완료되면 제공된 URL로 API를 사용할 수 있습니다.

## API 사용법
### 1. 문서 적재 (Ingestion)
*   **Endpoint:** `/api/v1/documents/ingest` (POST)
*   **Description:** `DOC` 폴더(또는 포함된 문서)를 벡터 DB에 적재.

### 2. 질문하기 (Chat)
*   **Endpoint:** `/api/v1/chat/completions` (POST)
*   **Body:** `{"question": "질문 내용"}`

## 주의사항
*   Render 무료 티어는 스핀다운(절전 모드)이 발생할 수 있습니다.
*   ChromaDB 데이터는 휘발성이므로, 배포된 컨테이너가 재시작되면 문서를 다시 적재해야 문답이 가능합니다.
