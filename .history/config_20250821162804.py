import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # OpenAI API 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # TTS 설정
    TTS_VOICE = "nova"
    TTS_MODEL = "tts-1"
    
    # 이미지 생성 설정
    IMAGE_MODEL = "dall-e-3"
    IMAGE_SIZE = "1024x1024"
    IMAGE_QUALITY = "standard"
    
    # 스토리 생성 설정
    STORY_MODEL = "gpt-4o"
    MAX_SCENES = 6
    
    # 추가 고급 설정
    STORY_TEMPERATURE = 0.8  # 창의성 조절
    STORY_MAX_TOKENS = 2000  # 더 긴 스토리 가능
    
    # 파일 저장 경로
    STATIC_DIR = "static"
    IMAGES_DIR = os.path.join(STATIC_DIR, "images")
    AUDIO_DIR = os.path.join(STATIC_DIR, "audio")

settings = Settings()

# 디렉토리 생성
os.makedirs(settings.IMAGES_DIR, exist_ok=True)
os.makedirs(settings.AUDIO_DIR, exist_ok=True)
