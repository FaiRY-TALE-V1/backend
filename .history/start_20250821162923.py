#!/usr/bin/env python3
"""
FaiRY TALE 백엔드 서버 시작 스크립트
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_requirements():
    """필수 패키지 설치 확인"""
    try:
        import fastapi
        import uvicorn
        import openai
        from dotenv import load_dotenv
        print(" 필수 패키지가 모두 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f" 필수 패키지가 누락되었습니다: {e}")
        print("pip install -r requirements.txt 명령어로 설치해주세요.")
        return False

def check_env_file():
    """환경변수 파일 확인"""
    env_file = project_root / ".env"
    if not env_file.exists():
        print(".env 파일이 없습니다.")
        print("1. .env.example을 복사하여 .env 파일을 만들어주세요.")
        print("2. .env 파일에서 OPENAI_API_KEY를 설정해주세요.")
        return False
    
    # OpenAI API 키 확인
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("OpenAI API 키가 설정되지 않았습니다.")
        print(".env 파일에서 OPENAI_API_KEY를 설정해주세요.")
        return False
    
    print("환경변수 설정이 완료되었습니다.")
    return True

def main():
    """서버 시작"""
    print("FaiRY TALE 백엔드 서버를 시작합니다...")
    print("=" * 50)
    
    # 필수 요구사항 확인
    if not check_requirements():
        return
    
    if not check_env_file():
        return
    
    print("서버를 시작합니다...")
    print("서버 주소: http://localhost:8000")
    print("API 문서: http://localhost:8000/docs")
    print("OpenAI API 사용")
    print("이미지 생성 제어: GENERATE_IMAGES=true/false")
    print("=" * 50)
    
    # 서버 시작
    try:
        import uvicorn
        
        uvicorn.run(
            "demo_main:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=True,
            timeout_keep_alive=30,
            timeout_graceful_shutdown=30
        )
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
    except Exception as e:
        print(f"서버 시작 실패: {e}")

if __name__ == "__main__":
    main()
