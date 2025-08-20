from fastapi import FastAPI, HTTPException, File, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import time
import openai
import base64
import uuid
from PIL import Image
import io

from models import (
    StoryRequest, CompleteStoryResponse, Theme,
    TTSRequest, TTSResponse
)
from openai_service import openai_story_service
from config import settings

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

# FastAPI 앱 생성
app = FastAPI(
    title="FaiRY TALE - 우리아이만의 동화책",
    description="OpenAI 기반 AI 개인화 동화 생성 서비스",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용: 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서비스 설정
if not os.path.exists("static"):
    os.makedirs("static")
    os.makedirs("static/images", exist_ok=True)
    os.makedirs("static/audio", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """API 서버 상태 확인"""
    openai_key_status = "✅ 설정됨" if settings.OPENAI_API_KEY else "❌ 미설정"
    
    return {
        "message": "🧚‍♀️ FaiRY TALE - 우리아이만의 동화책", 
        "version": "1.0.0",
        "status": "healthy",
        "models": {
            "text": "GPT-4o (OpenAI)",
            "image": "DALL-E 3 (OpenAI)", 
            "tts": "TTS-1 (OpenAI)"
        },
        "openai_api_key": openai_key_status,
        "description": "아이 맞춤형 AI 동화 생성 서비스"
    }

@app.get("/themes")
async def get_themes():
    """사용 가능한 테마 목록 조회"""
    themes = [
        {
            "value": "healthy_eating",
            "title": "식습관 개선",
            "emoji": "🥕",
            "label": "🥕 식습관 개선", 
            "description": "균형 잡힌 영양 섭취의 중요성을 배워요",
            "moral": "건강한 몸을 위해서는 다양한 음식을 골고루 먹어야 해요",
            "keywords": ["건강", "영양", "균형"],
            "color": "from-green-400 to-emerald-600",
            "bgColor": "bg-green-50",
            "examples": ["🥬 채소 친구들의 모험", "🍎 과일 왕국 여행", "🥛 우유와 칼슘 요정"]
        },
        {
            "value": "friendship_skills",
            "title": "교우관계",
            "emoji": "🤝", 
            "label": "🤝 교우관계",
            "description": "친구 사귀기와 갈등 해결 방법을 배워요",
            "moral": "진정한 우정은 서로를 이해하고 배려하는 마음에서 시작돼요",
            "keywords": ["우정", "화해", "소통"],
            "color": "from-blue-400 to-sky-600",
            "bgColor": "bg-blue-50",
            "examples": ["🌈 화해의 무지개", "🎭 새친구 환영 파티", "🤲 마음을 나누는 다리"]
        },
        {
            "value": "safety_habits",
            "title": "안전습관",
            "emoji": "🛡️",
            "label": "🛡️ 안전습관",
            "description": "일상 속에서 안전을 지키는 방법을 배워요", 
            "moral": "안전 수칙을 지키는 것은 나와 다른 사람을 보호하는 일이에요",
            "keywords": ["안전", "조심", "보호"],
            "color": "from-red-400 to-orange-600",
            "bgColor": "bg-red-50",
            "examples": ["🚦 신호등 친구의 가르침", "👮 안전 경찰관과 모험", "🏠 우리 집 안전 점검"]
        },
        {
            "value": "financial_literacy",
            "title": "경제관념",
            "emoji": "💰",
            "label": "💰 경제관념",
            "description": "용돈 관리와 저축하는 방법을 배워요",
            "moral": "계획적인 소비와 저축은 미래를 준비하는 지혜로운 습관이에요",
            "keywords": ["저축", "계획", "현명함"],
            "color": "from-yellow-400 to-amber-600",
            "bgColor": "bg-yellow-50",
            "examples": ["🐷 저금통 돼지의 여행", "💎 보물섬의 지혜", "🏪 꼬마 상인의 이야기"]
        },
        {
            "value": "emotional_intelligence",
            "title": "감정표현",
            "emoji": "💝",
            "label": "💝 감정표현",
            "description": "감정을 이해하고 올바르게 표현하는 방법을 배워요",
            "moral": "내 마음을 표현하고 다른 사람의 마음을 이해하는 것이 중요해요",
            "keywords": ["감정", "공감", "소통"],
            "color": "from-pink-400 to-rose-600",
            "bgColor": "bg-pink-50",
            "examples": ["😊 감정 요정들의 여행", "🤗 마음을 나누는 숲", "💕 위로의 마법사"]
        }
    ]
    return {"themes": themes}

@app.post("/generate_complete_story", response_model=CompleteStoryResponse)
async def generate_complete_story(request: StoryRequest, response: Response):
    """AI 기반 완전한 동화 생성 (사진 분석 포함)"""
    try:
        print(f"🎯 동화 생성 시작: {request.child_profile.name}, 테마: {request.theme}")
        
        # OpenAI API 키 확인
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API 키가 설정되지 않았습니다. 환경변수 OPENAI_API_KEY를 확인해주세요."
            )
        
        # 아이 사진 분석 (업로드된 경우)
        facial_features = None
        if request.child_profile.photo:
            try:
                print(f"📸 {request.child_profile.name}의 사진 분석 중...")
                facial_features = await openai_story_service.analyze_child_photo(
                    request.child_profile.photo,
                    request.child_profile.name, 
                    request.child_profile.age,
                    request.child_profile.gender
                )
                print(f"✅ 사진 분석 완료!")
            except Exception as e:
                print(f"⚠️ 사진 분석 실패, 기본값 사용: {str(e)}")
                facial_features = None
        
        # 동화 생성 서비스 호출 (사진 분석 결과 포함)
        result = await openai_story_service.generate_complete_story(request, facial_features)
        
        # 동화 생성 완료 후 연결 종료하여 timeout 방지
        response.headers["Connection"] = "close"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        
        print(f"🎉 동화 생성 완료: {result.story.title}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 동화 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"동화 생성 중 오류가 발생했습니다: {str(e)}")

@app.post("/generate_tts", response_model=TTSResponse)
async def generate_tts(request: TTSRequest):
    """OpenAI TTS를 사용한 음성 생성"""
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API 키가 설정되지 않았습니다."
            )
        
        print(f"🔊 장면 {request.scene_number} 음성 생성 중...")
        
        # OpenAI TTS API 호출
        response = client.audio.speech.create(
            model=settings.TTS_MODEL,
            voice=settings.TTS_VOICE,
            input=request.text
        )
        
        # 음성 파일 저장
        import uuid
        audio_filename = f"scene_{request.scene_number}_{uuid.uuid4().hex[:8]}.mp3"
        audio_path = os.path.join(settings.AUDIO_DIR, audio_filename)
        
        with open(audio_path, "wb") as audio_file:
            audio_file.write(response.content)
        
        audio_url = f"/static/audio/{audio_filename}"
        
        print(f"✅ 장면 {request.scene_number} 음성 생성 완료")
        
        return TTSResponse(
            audio_url=audio_url,
            scene_number=request.scene_number
        )
        
    except Exception as e:
        print(f"❌ 음성 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"음성 생성 실패: {str(e)}")

@app.post("/upload_photo")
async def upload_photo(file: UploadFile = File(...)):
    """아이 사진 업로드 API"""
    try:
        # 파일 타입 확인
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
        
        # 파일 크기 확인 (10MB 제한)
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 10MB 이하여야 합니다.")
        
        # 이미지 처리 및 리사이즈
        try:
            image = Image.open(io.BytesIO(contents))
            # RGB로 변환 (RGBA나 다른 형식 호환성)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 이미지 리사이즈 (최대 1024x1024)
            max_size = (1024, 1024)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Base64로 인코딩
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            image_data_url = f"data:image/jpeg;base64,{image_base64}"
            
            return {
                "success": True,
                "image_url": image_data_url,
                "message": "사진이 성공적으로 업로드되었습니다.",
                "file_info": {
                    "original_filename": file.filename,
                    "content_type": "image/jpeg",
                    "size": len(contents)
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"이미지 처리 중 오류가 발생했습니다: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 사진 업로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}")

@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    openai_key_status = "✅ 설정됨" if settings.OPENAI_API_KEY else "❌ 미설정"
    
    return {
        "service_name": "FaiRY TALE API",
        "status": "healthy",
        "models": {
            "text_generation": {
                "model": "GPT-4o",
                "provider": "OpenAI",
                "status": "✅ 사용 가능" if settings.OPENAI_API_KEY else "❌ API 키 미설정"
            },
            "image_generation": {
                "model": "DALL-E 3",
                "provider": "OpenAI", 
                "status": "✅ 사용 가능" if settings.OPENAI_API_KEY else "❌ API 키 미설정"
            },
            "tts_generation": {
                "model": "TTS-1",
                "provider": "OpenAI",
                "status": "✅ 사용 가능" if settings.OPENAI_API_KEY else "❌ API 키 미설정"
            }
        },
        "openai_api_key": openai_key_status,
        "features": [
            "개인화된 동화 생성",
            "AI 일러스트레이션",
            "TTS 음성 지원",
            "6개 장면 구성",
            "5가지 교육 테마",
            "사진 업로드 지원"
        ]
    }

if __name__ == "__main__":
    print("🧚‍♀️ FaiRY TALE - 우리아이만의 동화책 서버 시작!")
    print("📍 서버: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("🤖 AI 모델: GPT-4o + DALL-E 3 + TTS-1")
    print("💝 아이 맞춤형 동화 생성 서비스")
    print("🔑 OpenAI API 키 필요")
    print("💰 이미지 생성 제어: GENERATE_IMAGES=true/false")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
