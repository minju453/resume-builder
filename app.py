import logging
from api.index import app

logger = logging.getLogger(__name__)

# 로컬 개발 서버 실행 진입점 (python app.py)
if __name__ == "__main__":
    logger.info("Flask 웹 서버 시작 (포트: 5000)")
    app.run(host="127.0.0.1", port=5000, debug=True)
