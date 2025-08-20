import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Hugging Face API 키
    
    # TTS 설정
    TTS_VOICE = "alloy"  # OpenAI TTS voice options: alloy, echo, fable, onyx, nova, shimmer
    TTS_MODEL = "tts-1"
    
    # 이미지 생성 설정
    IMAGE_MODEL = "dall-e-3"
    IMAGE_SIZE = "1024x1024"
    IMAGE_QUALITY = "standard"
    
    # 스토리 생성 설정
    STORY_MODEL = "gpt-4o"  # GPT-4o 모델 사용
    MAX_SCENES = 6
    
    # 추가 고급 설정
    STORY_TEMPERATURE = 0.8  # 창의성 조절
    STORY_MAX_TOKENS = 2000  # 더 긴 스토리 가능
    
    # 파일 저장 경로
    STATIC_DIR = "static"
    IMAGES_DIR = os.path.join(STATIC_DIR, "images")
    AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
    
    # Qwen-Image-Edit 설정
    QWEN_MODEL_NAME = "Qwen/Qwen-Image-Edit"
    
    # 디바이스 자동 감지 (MPS > CUDA > CPU 순서)
    @property
    def QWEN_DEVICE(self):
        import torch
        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"
    
    @property        
    def QWEN_DTYPE(self):
        device = self.QWEN_DEVICE
        if device == "mps":
            return "float16"  # MPS는 float16이 더 안정적
        elif device == "cuda":
            return "bfloat16"
        else:
            return "float32"
    
    # 이미지 편집 기본 설정
    DEFAULT_INFERENCE_STEPS = 50
    DEFAULT_CFG_SCALE = 4.0
    DEFAULT_NEGATIVE_PROMPT = "low quality, blurry, dark, scary, inappropriate"

settings = Settings()

# 디렉토리 생성
os.makedirs(settings.IMAGES_DIR, exist_ok=True)
os.makedirs(settings.AUDIO_DIR, exist_ok=True)
