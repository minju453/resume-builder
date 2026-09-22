import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
import google.generativeai as genai

# 1. 환경변수(.env) 로드
load_dotenv()

# 2. 백엔드 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# 3. 디렉터리 경로 계산 (Vercel Lambda & 로컬 환경 2중 지원)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

# templates 및 static 경로 탐색
template_dir = os.path.join(ROOT_DIR, "templates") if os.path.exists(os.path.join(ROOT_DIR, "templates")) else os.path.join(CURRENT_DIR, "templates")
static_dir = os.path.join(ROOT_DIR, "static") if os.path.exists(os.path.join(ROOT_DIR, "static")) else os.path.join(CURRENT_DIR, "static")

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)

# 4. Vercel Serverless rewrite 경로 정규화 미들웨어
class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        for prefix in ["/api/index.py", "/api/index", "/api"]:
            if path == prefix:
                environ["PATH_INFO"] = "/"
                break
            elif path.startswith(prefix + "/"):
                environ["PATH_INFO"] = path[len(prefix):]
                break
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)

# 5. Gemini API Key 확인 및 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    logger.warning("경고: 유효한 GEMINI_API_KEY가 환경변수에 설정되지 않았습니다.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# 6. PWA 관련 라우트
@app.route("/manifest.json")
def manifest():
    return send_from_directory(static_dir, "manifest.json", mimetype="application/manifest+json")

@app.route("/sw.js")
def service_worker():
    return send_from_directory(static_dir, "sw.js", mimetype="application/javascript")

# 7. 메인 홈 화면 라우트
@app.route("/")
def index():
    logger.info("메인 페이지 요청 수신 (GET /)")
    return render_template("index.html")

# 8. 이력서 및 포트폴리오 생성 API 라우트
@app.route("/generate", methods=["POST"])
def generate():
    logger.info("이력서 및 포트폴리오 생성 요청 수신 (POST /generate)")

    current_key = os.getenv("GEMINI_API_KEY")
    if not current_key or current_key == "your_gemini_api_key_here":
        logger.error("오류: GEMINI_API_KEY가 설정되지 않았습니다.")
        return jsonify({
            "success": False,
            "error": "환경변수에 올바른 Gemini API Key가 설정되어 있지 않습니다. 키를 확인해 주세요."
        }), 500

    data = request.get_json()
    if not data:
        logger.warning("오류: 요청 본문에 JSON 데이터가 없습니다.")
        return jsonify({
            "success": False,
            "error": "전송된 데이터가 올바르지 않습니다."
        }), 400

    name = data.get("name", "").strip()
    job_title = data.get("job_title", "").strip()
    experience = data.get("experience", "").strip()
    projects = data.get("projects", "").strip()
    tone = data.get("tone", "professional").strip()
    prompt_type = data.get("prompt_type", "general").strip()

    if not name:
        return jsonify({"success": False, "error": "이름을 입력해 주세요."}), 400
    if not job_title:
        return jsonify({"success": False, "error": "지원 직무를 입력해 주세요."}), 400
    if not experience:
        return jsonify({"success": False, "error": "경력 사항을 입력해 주세요."}), 400
    if not projects:
        return jsonify({"success": False, "error": "주요 프로젝트 경험을 입력해 주세요."}), 400

    logger.info(f"요청자: {name}, 직무: {job_title}, 톤: {tone}, 모드: {prompt_type}")

    if prompt_type == "expert":
        system_instruction = (
            "당신은 글로벌 IT 대기업의 최고 인사담당자(Head of Talent Acquisition)이자 테크 리크루터입니다. "
            "지원자의 역량이 극대화되도록 성과 중심의 정량적 지표와 STAR(Situation, Task, Action, Result) 기법을 "
            "적용하여 전문적이고 설득력 있는 이력서와 포트폴리오를 작성해 주세요."
        )
    else:
        system_instruction = (
            "당신은 친절하고 전문적인 커리어 코치입니다. "
            "지원자의 장점과 성실성이 돋보이도록 깔끔하고 가독성이 높은 표준 이력서와 포트폴리오를 작성해 주세요."
        )

    prompt = f"""{system_instruction}

[지원자 정보]
- 이름: {name}
- 지원 직무: {job_title}
- 희망 어조(Tone): {tone}
- 경력 사항:
{experience}
- 주요 프로젝트:
{projects}

[작성 가이드라인]
1. 지원자의 정보를 바탕으로 완성도 높은 국문 '이력서(Resume)'와 '포트폴리오 요약본(Portfolio)'을 각각 작성해 주세요.
2. 결과물은 반드시 아래와 같이 [RESUME]와 [PORTFOLIO] 태그로 명확히 감싸서 출력해야 합니다.
3. 각 섹션 내부는 깔끔한 Markdown 형식(제목, 글머리 기호, 볼드체 등)으로 구조화해 주세요.

[출력 형식]
[RESUME]
# {name} - {job_title} 이력서
(이력서 본문 Markdown 내용)
[/RESUME]

[PORTFOLIO]
# {name} - 주요 프로젝트 포트폴리오
(포트폴리오 본문 Markdown 내용)
[/PORTFOLIO]
"""

    try:
        logger.info("Gemini API 호출 시작...")
        genai.configure(api_key=current_key)
        model = genai.GenerativeModel("gemini-3.5-flash-lite")
        response = model.generate_content(prompt)
        ai_text = response.text
        logger.info("Gemini API 응답 수신 완료")

        resume_content = ""
        portfolio_content = ""

        if "[RESUME]" in ai_text and "[/RESUME]" in ai_text:
            resume_content = ai_text.split("[RESUME]")[1].split("[/RESUME]")[0].strip()

        if "[PORTFOLIO]" in ai_text and "[/PORTFOLIO]" in ai_text:
            portfolio_content = ai_text.split("[PORTFOLIO]")[1].split("[/PORTFOLIO]")[0].strip()

        if not resume_content and not portfolio_content:
            resume_content = ai_text
            portfolio_content = "포트폴리오는 생성된 이력서 본문을 참고해 주세요."

        return jsonify({
            "success": True,
            "resume": resume_content,
            "portfolio": portfolio_content
        }), 200

    except Exception as e:
        logger.error(f"Gemini API 호출 중 오류 발생: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"AI 생성 중 오류가 발생했습니다: {str(e)}"
        }), 500
