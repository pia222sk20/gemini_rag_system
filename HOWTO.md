# RAG 시스템 실행 및 사용 가이드

## 1. 사전 준비 (필수)
이 시스템은 Docker 컨테이너 기반으로 동작하므로 로컬 가상환경(conda)과 무관하게 실행되지만, 명령어를 실행하는 환경은 중요합니다. 사용자는 이미 구성된 `conda rag_env` 환경 또는 일반 터미널 어디서든 `docker-compose` 명령어를 사용할 수 있습니다 (Docker Desktop이 설치되어 있어야 함).

### 환경 변수 설정
`c:/002.FINAL-PROJECT/.env` 파일에 `OPENAI_API_KEY`가 올바르게 입력되어 있는지 확인하세요.

## 2. 시스템 실행 (사용자 직접 실행)
시간이 오래 걸리는 빌드 작업을 직접 제어하고 로그를 확인하기 위해 터미널에서 다음 명령어를 실행해주세요.

```bash
cd c:/002.FINAL-PROJECT
docker-compose up --build
```
*   `--build`: 이미지를 새로 빌드합니다 (코드 변경 시 필수).
*   `-d` 옵션을 빼면 로그를 실시간으로 볼 수 있습니다. 백그라운드 실행을 원하면 `-d`를 붙이세요.

## 3. 시스템 구성 요소

### A. Backend (FastAPI)
*   **주소:** `http://localhost:8080/docs` (Swagger UI)
*   **기능:** 문서 적재 및 채팅 API 제공.

### B. ChromaDB (Vector Database)
*   **주소:** `http://localhost:8000/docs` (Swagger UI - 사용자가 확인한 화면)
*   **역할:** 벡터 데이터 저장 및 검색. 백엔드가 내부적으로 통신하므로 사용자가 직접 호출할 일은 드뭅니다.

## 4. API 사용 방법 (순서대로 진행)

시스템이 실행 중인 상태에서 Swagger UI(`http://localhost:8080/docs`)를 통해 테스트하거나, `curl` / `Postman` 등을 사용하여 직접 요청할 수 있습니다.

### [Step 1] 문서 적재 (Ingestion)
준비된 문서(PDF, DOCX, TXT 등)를 `DOC` 폴더에 넣은 후, 이 API를 호출하여 벡터 DB에 저장합니다.

*   **URL:** `POST http://localhost:8080/api/v1/documents/ingest`
*   **설명:** `DOC` 폴더를 스캔하여 자동으로 적재합니다.
*   **Curl 예시:**
    ```bash
    curl -X 'POST' \
      'http://localhost:8080/api/v1/documents/ingest' \
      -H 'accept: application/json' \
      -d ''
    ```

### [Step 2] 질문하기 (Chat)
문서 적재가 완료되면, 문서 내용을 바탕으로 질문을 던집니다.

*   **URL:** `POST http://localhost:8080/api/v1/chat/completions`
*   **Body:**
    ```json
    {
      "question": "Google Antigravity가 무엇인가요?"
    }
    ```
*   **Curl 예시:**
    ```bash
    curl -X 'POST' \
      'http://localhost:8080/api/v1/chat/completions' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "question": "Google Antigravity가 무엇인가요?"
    }'
    ```

## 5. 문제 해결
*   **Docker 실행 오류:** Docker Desktop이 켜져 있는지 확인하세요.
*   **API Key 오류:** `.env` 파일 저장 후 `docker-compose up`을 다시 실행해야 적용됩니다.
