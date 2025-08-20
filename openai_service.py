import openai
import os
import uuid
import time
import json
from typing import Dict, Any
from config import settings
from models import (
    StoryRequest, Story, StoryScene, CompleteStoryResponse
)

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIStoryService:
    """OpenAI 모델들을 사용한 완전한 동화 생성 서비스"""
    
    def __init__(self):
        pass
    
    def generate_story_prompt(self, child_name: str, child_age: int, theme: str) -> str:
        """테마별 동화 생성 프롬프트 작성"""
        
        theme_guidelines = {
            "식습관 개선": {
                "context": "건강한 식습관의 중요성을 배우는",
                "key_lessons": ["다양한 음식 골고루 먹기", "편식하지 않기", "건강한 간식 선택"],
                "characters": "영양소 요정들, 건강한 음식 친구들",
                "setting": "마법의 음식 나라나 건강 레스토랑"
            },
            "교우관계": {
                "context": "친구들과의 올바른 관계 형성을 배우는",
                "key_lessons": ["배려와 나눔", "협력의 중요성", "다름 인정하기"],
                "characters": "다양한 성격의 친구들, 지혜로운 선생님",
                "setting": "학교, 놀이터, 친구들과의 모험"
            },
            "안전습관": {
                "context": "일상생활에서의 안전 수칙을 배우는",
                "key_lessons": ["교통안전 지키기", "화재 예방", "놀이 안전"],
                "characters": "안전 수호천사, 경찰관, 소방관",
                "setting": "집, 학교, 길거리, 놀이터"
            },
            "경제관념": {
                "context": "돈의 소중함과 올바른 소비 습관을 배우는",
                "key_lessons": ["저축의 중요성", "필요와 욕구 구분", "계획적 소비"],
                "characters": "돼지 저금통, 은행원, 현명한 할머니",
                "setting": "상점, 은행, 집안에서의 용돈 관리"
            },
            "감정표현": {
                "context": "자신의 감정을 올바르게 표현하는 방법을 배우는",
                "key_lessons": ["감정 인식하기", "건전한 표현 방법", "타인 감정 이해"],
                "characters": "감정 요정들, 이해심 많은 가족",
                "setting": "가정, 감정의 정원, 마음의 세계"
            }
        }
        
        current_theme = theme_guidelines.get(theme, theme_guidelines["교우관계"])
        
        prompt = f"""
당신은 세계적으로 유명한 아동문학 작가입니다. 다음 조건에 맞는 감동적이고 교육적인 동화를 창작해주세요.

📚 작품 정보:
- 주인공: {child_name} ({child_age}세)
- 교육 테마: {theme}
- 목표: {current_theme['context']} 동화

🎯 핵심 교훈: {', '.join(current_theme['key_lessons'])}

🌟 창작 가이드라인:
1. 연령 적합성: {child_age}세 아이의 언어 발달과 이해력에 맞춘 어휘와 문장 구조
2. 몰입감: {child_name}이 주인공이 되어 직접 경험하는 듯한 생생한 묘사
3. 교육적 가치: {theme}의 중요성을 강요하지 않고 자연스럽게 깨달을 수 있는 스토리
4. 감정적 연결: 아이가 공감할 수 있는 상황과 감정 변화
5. 긍정적 결말: 성장과 배움을 통한 희망적이고 따뜻한 마무리

🎭 등장인물 활용: {current_theme['characters']}
🏞️ 배경 설정: {current_theme['setting']}

📖 구성 요구사항:
- 총 6개 장면으로 구성
- 각 장면: 2-3문장 (아이가 이해하기 쉬운 길이)
- 장면별 명확한 전개와 교훈 연결
- DALL-E 3용 상세한 영어 이미지 프롬프트 포함

응답 형식 (JSON):
{{
    "title": "매력적이고 교육적인 동화 제목",
    "scenes": [
        {{
            "scene_number": 1,
            "text": "생생하고 몰입감 있는 장면 서술",
            "image_prompt": "Detailed English prompt for DALL-E 3: children's book illustration, watercolor style, showing [specific scene description], warm colors, age-appropriate, Korean child, educational theme"
        }}
    ]
}}
"""
        return prompt
    
    async def generate_story_with_gpt4o_mini(self, request: StoryRequest) -> Dict[str, Any]:
        """GPT-4o-mini를 사용한 스토리 생성"""
        try:
            print(f"📝 GPT-4o-mini로 스토리 생성 중...")
            
            prompt = self.generate_story_prompt(
                request.child_profile.name,
                request.child_profile.age,
                request.theme
            )
            
            response = client.chat.completions.create(
                model=settings.STORY_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 세계적으로 유명한 아동문학 작가입니다. 교육적 가치와 재미를 모두 갖춘 감동적인 동화를 창작하세요. 응답은 반드시 유효한 JSON 형식으로 해주세요."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            story_text = response.choices[0].message.content
            print(f"GPT-4o-mini 응답: {story_text[:200]}...")
            
            # JSON 파싱
            try:
                json_start = story_text.find('{')
                json_end = story_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_text = story_text[json_start:json_end]
                    story_data = json.loads(json_text)
                    print(f"✅ 스토리 생성 완료: {story_data.get('title', '제목 없음')}")
                    return story_data
                else:
                    raise ValueError("JSON 형식을 찾을 수 없습니다")
            except Exception as e:
                print(f"⚠️ JSON 파싱 실패: {str(e)}")
                # 기본 구조 반환
                return {
                    "title": f"{request.child_profile.name}의 {request.theme} 이야기",
                    "scenes": [
                        {
                            "scene_number": 1,
                            "text": f"{request.child_profile.name}는 {request.theme}에 대해 배우기 시작했어요.",
                            "image_prompt": f"Children's book illustration of a Korean child learning about {request.theme}"
                        }
                    ]
                }
                
        except Exception as e:
            print(f"❌ GPT-4o-mini 스토리 생성 실패: {str(e)}")
            raise e
    
    async def generate_image_with_dalle3(self, image_prompt: str, scene_number: int) -> str:
        """DALL-E 3를 사용한 이미지 생성"""
        try:
            print(f"🎨 DALL-E 3로 장면 {scene_number} 이미지 생성 중...")
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            print(f"✅ 장면 {scene_number} 이미지 생성 완료")
            return image_url
            
        except Exception as e:
            print(f"❌ DALL-E 3 이미지 생성 실패: {str(e)}")
            # 실패시 플레이스홀더 이미지 반환
            return f"https://picsum.photos/400/300?random={scene_number}&blur=1"
    
    async def generate_audio_with_tts1(self, text: str, scene_number: int, child_name: str) -> str:
        """OpenAI TTS-1을 사용한 음성 생성"""
        try:
            print(f"🔊 TTS-1로 장면 {scene_number} 음성 생성 중...")
            
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",  # 아이들에게 적합한 목소리
                input=text
            )
            
            # 음성 파일 저장
            audio_filename = f"scene_{scene_number}_{child_name}_{int(time.time())}.mp3"
            audio_path = os.path.join(settings.AUDIO_DIR, audio_filename)
            
            with open(audio_path, "wb") as audio_file:
                audio_file.write(response.content)
            
            audio_url = f"/static/audio/{audio_filename}"
            print(f"✅ 장면 {scene_number} 음성 생성 완료")
            return audio_url
            
        except Exception as e:
            print(f"❌ TTS-1 음성 생성 실패: {str(e)}")
            return ""  # 실패시 빈 문자열
    
    async def generate_complete_story(self, request: StoryRequest) -> CompleteStoryResponse:
        """OpenAI 모델들을 사용한 완전한 동화 생성"""
        try:
            print(f"🚀 OpenAI 완전 동화 생성 시작: {request.child_profile.name}, 테마: {request.theme}")
            
            # 1. GPT-4o-mini로 스토리 생성
            story_data = await self.generate_story_with_gpt4o_mini(request)
            
            # 2. 각 장면별 이미지 및 음성 생성
            scenes = []
            for scene_data in story_data.get("scenes", [])[:6]:  # 최대 6개 장면
                scene_num = scene_data.get("scene_number", len(scenes) + 1)
                scene_text = scene_data.get("text", "")
                image_prompt = scene_data.get("image_prompt", f"Children's book illustration, scene {scene_num}")
                
                # DALL-E 3로 이미지 생성 (비용 절약을 위해 선택적으로)
                if os.getenv("GENERATE_IMAGES", "false").lower() == "true":
                    image_url = await self.generate_image_with_dalle3(image_prompt, scene_num)
                else:
                    # 플레이스홀더 이미지 사용 (비용 절약)
                    colors = ["8B5CF6", "EC4899", "F59E0B", "10B981", "3B82F6", "8B5A2B"]
                    color = colors[scene_num % len(colors)]
                    image_url = f"https://picsum.photos/400/300?random={scene_num}&blur=1"
                    print(f"💰 비용 절약을 위해 장면 {scene_num}에 플레이스홀더 이미지 사용")
                
                # TTS-1로 음성 생성
                audio_url = await self.generate_audio_with_tts1(scene_text, scene_num, request.child_profile.name)
                
                scene = StoryScene(
                    scene_number=scene_num,
                    text=scene_text,
                    image_url=image_url,
                    audio_url=audio_url
                )
                scenes.append(scene)
            
            # 3. 최종 스토리 구성
            story = Story(
                title=story_data.get("title", f"{request.child_profile.name}의 {request.theme} 이야기"),
                scenes=scenes
            )
            
            # 캐릭터 이미지도 생성 (선택적)
            if os.getenv("GENERATE_IMAGES", "false").lower() == "true":
                character_prompt = f"Children's book character illustration of {request.child_profile.name}, a {request.child_profile.age}-year-old Korean {request.child_profile.gender}, watercolor style, friendly and warm"
                character_image = await self.generate_image_with_dalle3(character_prompt, 0)
            else:
                character_image = f"https://picsum.photos/400/400?random=character&blur=2"
            
            response = CompleteStoryResponse(
                story=story,
                character_image=character_image,
                total_scenes=len(scenes)
            )
            
            print(f"🎉 OpenAI 완전 동화 생성 완료! '{story.title}' (총 {len(scenes)}개 장면)")
            return response
            
        except Exception as e:
            print(f"❌ OpenAI 완전 동화 생성 실패: {str(e)}")
            raise e

# 전역 서비스 인스턴스
openai_story_service = OpenAIStoryService()
