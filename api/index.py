import os
import sys

# 프로젝트 루트 경로를 sys.path에 추가 (모듈 import 호환성 확보)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel Serverless Entrypoint
# app 객체를 WSGI 애플리케이션으로 노출
