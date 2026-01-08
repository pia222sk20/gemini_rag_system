# Firebase & Cloud Run 배포 가이드 (Project ID: rag-prg)

## 1. 프로젝트 폴더 이동
모든 명령어는 프로젝트 루트 폴더에서 실행해야 합니다.
```bash
cd c:\002.FINAL-PROJECT
```

## 2. Cloud Run 배포 (백엔드)

### A. 프로젝트 설정
```bash
gcloud config set project rag-prg
```

### B. 도커 이미지 빌드 및 업로드
Google Cloud Build를 사용하여 이미지를 빌드하고 Container Registry에 저장합니다.
```bash
gcloud builds submit --tag gcr.io/rag-prg/rag-backend
```

### C. 서비스 배포
Cloud Run에 서비스를 배포합니다. **반드시 아래 명령어의 `OPENAI_API_KEY` 값을 실제 키로 변경 후 실행하세요.**
```bash
gcloud run deploy rag-backend \
  --image gcr.io/rag-prg/rag-backend \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
```
*   `--region asia-northeast3`: 서울 리전
*   `--allow-unauthenticated`: 외부 접속 허용 (테스트용)

## 3. Firebase Hosting 배포 (프록시)
Cloud Run 배포가 완료되면, Firebase Hosting을 통해 깔끔한 URL로 연결합니다.

```bash
# 프로젝트 연결 확인 (필요시)
firebase use --add rag-prg

# 호스팅 배포
firebase deploy --only hosting
```

## 4. 접속 확인
배포 후 출력되는 Hosting URL (`https://rag-prg.web.app`)을 통해 API를 사용할 수 있습니다.
*   **API 엔드포인트:** `https://rag-prg.web.app/api/v1/chat/completions`
*   **참고:** `/docs` (Swagger UI)는 FastAPI 설정에 따라 Firebase Hosting 경로에서 바로 안 보일 수도 있습니다. (직접 Cloud Run URL로 접속하면 보임)
