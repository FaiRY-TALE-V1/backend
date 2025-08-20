from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Theme(str, Enum):
    HEALTHY_EATING = "식습관 개선"
    FRIENDSHIP_SKILLS = "교우관계"
    SAFETY_HABITS = "안전습관"
    FINANCIAL_LITERACY = "경제관념"
    EMOTIONAL_INTELLIGENCE = "감정표현"

class ChildProfile(BaseModel):
    name: str
    age: int
    gender: Optional[str] = "boy"  # "boy" | "girl"
    photo: Optional[str] = None  # base64 encoded image or file path

class StoryRequest(BaseModel):
    child_profile: ChildProfile
    theme: str  # 문자열로 받아서 처리

class StoryScene(BaseModel):
    scene_number: int
    text: str
    image_url: Optional[str] = ""  # 이미지 URL 또는 Base64
    audio_url: Optional[str] = ""  # 오디오 URL
    image_prompt: Optional[str] = ""  # 기존 호환성 유지

class Story(BaseModel):
    title: str
    scenes: List[StoryScene]

class CompleteStoryResponse(BaseModel):
    story: Story
    character_image: Optional[str] = ""  # 생성된 캐릭터 이미지
    total_scenes: int

class ImageRequest(BaseModel):
    scene_text: str
    child_name: str
    child_age: int
    style_prompt: str

class ImageResponse(BaseModel):
    image_url: str
    scene_number: int

class TTSRequest(BaseModel):
    text: str
    scene_number: int

class TTSResponse(BaseModel):
    audio_url: str
    scene_number: int

# Qwen-Image-Edit 관련 모델들
class ImageEditRequest(BaseModel):
    image: str  # Base64 encoded image
    prompt: str
    negative_prompt: Optional[str] = ""
    num_inference_steps: Optional[int] = 50
    true_cfg_scale: Optional[float] = 4.0

class CharacterGenerationRequest(BaseModel):
    child_photo: str  # Base64 encoded photo
    child_name: str
    age: int
    gender: str  # "boy" | "girl"
    theme: str

class PersonalizedSceneRequest(BaseModel):
    character_image: str
    scene_description: str
    child_name: str
    theme: str

class ImageEditResponse(BaseModel):
    edited_image: str  # Base64 encoded image
    processing_time: float
    success: bool
    error_message: Optional[str] = None
