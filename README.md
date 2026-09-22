# 🚀 AI Resume & Portfolio Builder

Google Gemini AI를 활용하여 사용자의 이름, 지원 직무, 경력, 프로젝트 경험을 바탕으로 맞춤형 국문 **이력서(Resume)**와 **포트폴리오(Portfolio)**를 자동 생성해 주는 풀스택 웹 애플리케이션입니다.

---

## 🌟 주요 기능 (Key Features)

1. **맞춤형 정보 입력 폼**
   - 이름, 지원 직무, 문체/어조(Tone), 경력 사항, 주요 프로젝트 경험 입력 지원
2. **듀얼 프롬프트 엔진 (Prompt Engineering)**
   - **Prompt A (일반 모드):** 균형 잡히고 깔끔하며 자연스러운 표준 서술형
   - **Prompt B (전문가 모드):** 수치 및 성과 중심, 글로벌 IT 기업 STAR(Situation, Task, Action, Result) 기법 적용
3. **Google Gemini 최신 AI 모델 연동**
   - 최신 초경량 고속 모델인 `gemini-3.5-flash-lite`를 탑재하여 빠르고 안정적인 무료 생성 지원
4. **리치 마크다운(Markdown) 뷰어 및 커스텀 디자인**
   - `marked.js` 기반 서식 렌더링 (제목, 목록, 인용구 등)
   - 주요 강조 키워드(Bold) 핑크색(`#ec4899`) 하이라이트
   - 눈이 편안한 따뜻한 파스텔 옐로우(`#fef9c3`) 테마
5. **원클릭 편의 기능**
   - **📋 클립보드 복사:** 원본 마크다운 텍스트를 클립보드로 즉시 복사
   - **💾 .md 파일 다운로드:** `지원자이름_이력서.md`, `지원자이름_포트폴리오.md` 파일로 내 컴퓨터에 바로 저장
6. **철저한 보안 및 안정성**
   - Frontend 및 Backend 양방향 유효성 검증
   - `.env` 및 `.gitignore`를 통한 Gemini API Key 노출 원천 차단
   - 백엔드 실시간 요청 및 오류 로깅(Logging)

---

## 🛠 기술 스택 (Tech Stack)

| 구분 | 기술 / 라이브러리 |
| :--- | :--- |
| **Backend** | Python 3.x, Flask, google-generativeai, python-dotenv |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla JS), Marked.js |
| **AI Model** | Google Gemini API (`gemini-3.5-flash-lite`) |
| **Environment** | Windows PowerShell, Python venv, Git |

---

## 📂 프로젝트 구조 (Project Structure)

```text
resume-builder/
├── app.py                  # Flask 백엔드 서버 및 Gemini API 연동
├── requirements.txt        # 파이썬 필수 패키지 목록
├── .env                    # 실제 API Key (Git 제외)
├── .env.example            # 환경변수 템플릿 견본
├── .gitignore              # Git 추적 제외 설정
├── README.md               # 프로젝트 설명서
├── templates/
│   └── index.html          # 메인 웹 페이지 템플릿
└── static/
    ├── css/
    │   └── style.css       # 스타일시트 (파스텔 옐로우 & 핑크 포인트)
    └── js/
        └── app.js          # 프론트엔드 비동기 통신, 마크다운 렌더링, 복사/다운로드
```

---

## 🚀 빠른 시작 가이드 (Getting Started)

Windows PowerShell 기준으로 아래 순서대로 실행합니다.

### 1. 가상환경 활성화
```powershell
Set-Location "C:\AI-study\resume-builder"
.\venv\Scripts\Activate.ps1
```

### 2. 패키지 설치 (최초 1회)
```powershell
py -m pip install -r requirements.txt
```

### 3. API Key 설정
`.env.example`을 복사하여 `.env` 파일을 만들고, [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급받은 API 키를 입력합니다.
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. 웹 서버 실행
```powershell
py app.py
```

### 5. 브라우저 접속
웹 브라우저(Chrome, Edge 등)를 열고 아래 주소로 접속합니다:
👉 **`http://127.0.0.1:5000`**

---

## 🔒 보안 주의사항 (Security)

- `.env` 파일에는 개인 API 키가 들어있으므로 절대로 GitHub 등 공개 저장소에 업로드하지 마세요.
- `.gitignore`에 `.env`와 `venv/`가 이미 등록되어 있어 안전하게 관리됩니다.

---

## 📝 라이선스 (License)

This project is created for educational and personal portfolio purposes.
