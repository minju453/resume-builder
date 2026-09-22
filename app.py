import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
import google.generativeai as genai

# 1. 환경변수(.env) 로드
load_dotenv()

# 2. 백엔드 로깅(Logging) 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# 3. Flask 웹 애플리케이션 생성 (Vercel Serverless 절대경로 호환)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# 4. Gemini API Key 확인 및 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    logger.warning("경고: 유효한 GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# 5. PWA 관련 라우트 (루트 스코프 제공)
@app.route("/manifest.json")
def manifest():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "manifest.json", mimetype="application/manifest+json")

@app.route("/sw.js")
def service_worker():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "sw.js", mimetype="application/javascript")

# 6. 메인 홈 화면 라우트 (GET /)
@app.route("/")
def index():
    logger.info("메인 페이지 요청 수신 (GET /)")
    return render_template("index.html")

# 6. 이력서 및 포트폴리오 생성 API 라우트 (POST /generate)
@app.route("/generate", methods=["POST"])
def generate():
    logger.info("이력서 및 포트폴리오 생성 요청 수신 (POST /generate)")

    # API Key 검증
    current_key = os.getenv("GEMINI_API_KEY")
    if not current_key or current_key == "your_gemini_api_key_here":
        logger.error("오류: GEMINI_API_KEY가 설정되지 않았습니다.")
        return jsonify({
            "success": False,
            "error": ".env 파일에 올바른 Gemini API Key가 설정되어 있지 않습니다. 키를 확인해 주세요."
        }), 500

    # 요청 데이터(JSON) 수신
    data = request.get_json()
    if not data:
        logger.warning("오류: 요청 본문에 JSON 데이터가 없습니다.")
        return jsonify({
            "success": False,
            "error": "전송된 데이터가 올바르지 않습니다."
        }), 400

    # 필수 입력값 추출
    name = data.get("name", "").strip()
    job_title = data.get("job_title", "").strip()
    experience = data.get("experience", "").strip()
    projects = data.get("projects", "").strip()
    tone = data.get("tone", "professional").strip()
    prompt_type = data.get("prompt_type", "general").strip()

    # 백엔드 입력 검증 (Validation)
    if not name:
        logger.warning("검증 실패: 이름이 누락되었습니다.")
        return jsonify({"success": False, "error": "이름을 입력해 주세요."}), 400

    if not job_title:
        logger.warning("검증 실패: 지원 직무가 누락되었습니다.")
        return jsonify({"success": False, "error": "지원 직무를 입력해 주세요."}), 400

    if not experience:
        logger.warning("검증 실패: 경력 사항이 누락되었습니다.")
        return jsonify({"success": False, "error": "경력 사항을 입력해 주세요."}), 400

    if not projects:
        logger.warning("검증 실패: 프로젝트 경험이 누락되었습니다.")
        return jsonify({"success": False, "error": "주요 프로젝트 경험을 입력해 주세요."}), 400

    logger.info(f"요청자: {name}, 지원 직무: {job_title}, 톤: {tone}, 프롬프트 유형: {prompt_type}")

    # 프롬프트 엔지니어링 (Prompt A vs Prompt B)
    if prompt_type == "expert":
        # Prompt B: 전문가 모드 (성과 중심, STAR 기법 기반)
        system_instruction = (
            "당신은 글로벌 IT 대기업의 최고 인사담당자(Head of Talent Acquisition)이자 테크 리크루터입니다. "
            "지원자의 역량이 극대화되도록 성과 중심의 정량적 지표와 STAR(Situation, Task, Action, Result) 기법을 "
            "적용하여 전문적이고 설득력 있는 이력서와 포트폴리오를 작성해 주세요."
        )
    else:
        # Prompt A: 일반 모드 (균형 잡히고 깔끔한 표준 서술형)
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
        
        # 최신 Gemini 모델 인스턴스화
        model = genai.GenerativeModel("gemini-3.5-flash-lite")
        
        response = model.generate_content(prompt)
        ai_text = response.text
        logger.info("Gemini API 응답 수신 완료")

        # 결과 텍스트 파싱 ([RESUME], [PORTFOLIO] 분리)
        resume_content = ""
        portfolio_content = ""

        if "[RESUME]" in ai_text and "[/RESUME]" in ai_text:
            resume_content = ai_text.split("[RESUME]")[1].split("[/RESUME]")[0].strip()
        
        if "[PORTFOLIO]" in ai_text and "[/PORTFOLIO]" in ai_text:
            portfolio_content = ai_text.split("[PORTFOLIO]")[1].split("[/PORTFOLIO]")[0].strip()

        # 태그 파싱이 실패했을 때의 대비책
        if not resume_content and not portfolio_content:
            resume_content = ai_text
            portfolio_content = "포트폴리오는 생성된 이력서 본문을 참고해 주세요."

        logger.info("이력서 및 포트폴리오 생성 성공")
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

# 7. 서버 실행 진입점
if __name__ == "__main__":
    logger.info("Flask 웹 서버 시작 (포트: 5000)")
    app.run(host="127.0.0.1", port=5000, debug=True)
