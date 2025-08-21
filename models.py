from pydantic import BaseModel
from typing import Optional, List


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


