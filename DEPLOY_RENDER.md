# Render 무료 배포 가이드

Google Cloud 결제 등록 없이, GitHub와 Render.com을 연동하여 무료로 배포하는 방법입니다.

## 1단계: GitHub 저장소 만들기
1.  [GitHub](https://github.com)에 로그인하고 **New Repository**를 생성합니다 (예: `rag-project`).
2.  터미널에서 프로젝트 폴더(`c:\002.FINAL-PROJECT`)로 이동 후 코드를 푸시합니다.

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
# 아래 URL은 본인의 저장소 주소로 변경하세요!
git remote add origin https://github.com/YOUR_USERNAME/rag-project.git
git push -u origin main
```

## 2단계: Render.com 설정
1.  [Render.com](https://render.com)에 접속하여 **Sign up with GitHub**으로 가입/로그인합니다.
2.  대시보드에서 **New +** 버튼 클릭 -> **Web Service** 선택.
3.  **Connect a repository** 목록에서 방금 올린 `rag-project`를 선택해 **Connect** 클릭.

## 3단계: 배포 설정 입력
다음 설정값들을 입력하고 페이지 하단의 **Create Web Service**를 클릭합니다.

*   **Name:** `rag-service` (원하는 이름)
*   **Region:** Singapore (그나마 한국과 가까움)
*   **Runtime:** **Docker** (중요! Dockerfile을 감지합니다)
*   **Instance Type:** Free

### 환경 변수 설정 (Environment Variables)
**Advanced** 버튼을 누르거나 생성 후 **Environment** 탭에서 추가합니다.
*   **Key:** `OPENAI_API_KEY`
*   **Value:** `sk-...` (사용자의 실제 OpenAI 키)

## 4단계: 완료 및 테스트
배포가 완료되면(약 3~5분 소요), 상단에 `https://rag-service.onrender.com` 같은 URL이 생성됩니다.

*   **Swagger UI:** `https://[앱-URL]/docs`
*   **채팅 API:** `https://[앱-URL]/api/v1/chat/completions`

### 주의사항
*   무료 티어는 15분간 요청이 없으면 **Sleep Mode**로 들어갑니다. 다시 접속할 때 첫 응답이 30초 정도 걸릴 수 있습니다.
*   ChromaDB 데이터는 휘발성입니다 (서버 재시작 시 초기화). 지속적인 저장을 위해서는 외부 DB 서비스가 필요합니다.
