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
from typing import Tuple

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIStoryService:
    """OpenAI 모델들을 사용한 완전한 동화 생성 서비스"""
    
    def __init__(self):
        pass
    
    async def analyze_child_photo(self, photo_base64: str, child_name: str, child_age: int, child_gender: str) -> str:
        """업로드된 아이 사진을 분석하여 얼굴 특징 추출"""
        try:
            print(f"📸 {child_name}의 사진 분석 중...")
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""As an art director creating a children's book character, please analyze the visual characteristics in this illustration reference for creating a consistent animated character design.

Please provide a character design description in English that includes:
- Face shape and proportions
- Eye style and expression  
- Hair design and color
- Overall appearance style
- Clothing or outfit suggestions

This is for creating a consistent illustrated character across multiple scenes in an educational children's storybook. The character should be age-appropriate for a {child_age}-year-old child.

Format example: "round friendly face, large expressive eyes, neat hair style, casual children's clothing, warm and approachable appearance"

This analysis will be used purely for artistic character consistency in children's educational content."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": photo_base64
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.3  # 일관성을 위해 낮은 temperature
            )
            
            facial_features = response.choices[0].message.content
            print(f"✅ 얼굴 특징 분석 완료: {facial_features[:100]}...")
            return facial_features
            
        except Exception as e:
            print(f"❌ 사진 분석 실패: {str(e)}")
            # 기본값 반환
            return f"Korean {child_gender}, {child_age} years old, round face, big expressive eyes, short black hair, fair skin, cheerful expression"

    def generate_detailed_character_description(self, child_name: str, child_age: int, child_gender: str, facial_features: str = None) -> str:
        """상세한 캐릭터 디스크립션 생성 (DALL-E 3용)"""
        if facial_features and "sorry" not in facial_features.lower():
            # 사진 분석이 성공한 경우
            base_features = facial_features
        else:
            # 기본 한국 아이 특징 사용
            if child_gender.lower() in ['여자', 'female', 'girl']:
                base_features = "round face, big expressive dark eyes, straight black hair with bangs, fair skin tone, small nose, gentle smile, innocent expression"
            else:
                base_features = "round face, big expressive dark eyes, short black hair, fair skin tone, small nose, cheerful smile, bright expression"
        
        return f"Korean {child_age}-year-old {child_gender}, {base_features}, wearing simple casual children's clothes"
    
    def enhance_prompt_for_consistency(self, base_prompt: str, character_description: str, scene_number: int) -> str:
        """캐릭터 일관성을 위한 강화된 프롬프트 생성"""
        consistency_keywords = [
            "CONSISTENT CHARACTER:",
            "SAME CHILD IN ALL SCENES:",
            "IDENTICAL APPEARANCE:",
            "WATERCOLOR CHILDREN'S BOOK STYLE:",
            "SOFT PASTEL COLORS:",
            "2D ILLUSTRATION:",
        ]
        
        enhanced_prompt = f"""
{consistency_keywords[scene_number % len(consistency_keywords)]} {character_description}

SCENE DESCRIPTION: {base_prompt}

STYLE REQUIREMENTS: 
- Soft watercolor children's book illustration
- Consistent 2D art style (not 3D)
- Warm pastel color palette (coral pink, soft blue, cream yellow, light green)
- Child-friendly, gentle lighting
- The main character must look EXACTLY the same as in previous scenes
- Same facial features, hair style, clothing throughout the story
"""
        
        return enhanced_prompt.strip()

    def generate_character_style_guide(self, child_name: str, child_age: int, child_gender: str, facial_features: str = None) -> str:
        """캐릭터 일관성을 위한 스타일 가이드 생성 (사진 분석 결과 포함)"""
        if facial_features:
            character_description = facial_features
        else:
            character_description = f"Korean {child_gender}, {child_age} years old, round face, big expressive eyes, short black hair, fair skin"
            
        return f"""
CONSISTENT CHARACTER STYLE GUIDE for {child_name}:
- Main character: {child_name}, {child_age} years old Korean {child_gender}
- Character physical features: {character_description}
- Art style: Soft watercolor children's book illustration, consistent across all scenes
- Drawing style: Consistent 2D illustration style, not 3D, similar to classic children's storybooks  
- Character should look EXACTLY the same in every scene with identical facial features, hair, and appearance
- Color palette: Warm, soft pastels that complement the child's features
- Background style: Simple, clean, child-friendly environments
- Lighting: Soft, warm natural lighting throughout all scenes
- Clothing: Simple, age-appropriate casual clothes that stay consistent
"""

    def generate_story_prompt(self, child_name: str, child_age: int, child_gender: str, theme: str, facial_features: str = None) -> str:
        """테마별 동화 생성 프롬프트 작성 (사진 분석 결과 포함)"""
        
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
        style_guide = self.generate_character_style_guide(child_name, child_age, child_gender, facial_features)
        
        # 감정표현 테마 전용 스토리 다양성 요소
        import random
        emotion_themes = [
            "기쁨과 슬픔을 균형있게 표현하는", "화가 날 때 올바르게 대처하는", 
            "무서움을 극복하는", "부끄러움을 이겨내는", "실망감을 다루는", "질투심을 조절하는"
        ]
        random_emotion = random.choice(emotion_themes)
        
        emotion_scenarios = [
            "감정 요정들을 만나는", "마음의 정원을 가꾸는", "감정 색깔을 찾는",
            "마음의 날씨를 바꾸는", "감정 동물 친구들과 놀이하는", "마음의 보석을 찾는"
        ]
        emotion_scenario = random.choice(emotion_scenarios)
        
        prompt = f"""
당신은 세계적으로 유명한 아동문학 작가입니다. 감정표현을 주제로 한 감동적이고 교육적인 동화를 창작해주세요.

🎨 감정표현 스토리: {random_emotion} 방법을 배우는 {emotion_scenario} 이야기로 만들어주세요.
📖 매번 다른 제목과 내용으로 창작해주세요 (템플릿 사용 금지).

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
            "image_prompt": "CONSISTENT STYLE: Soft watercolor children's book illustration. {child_name}, {child_age}-year-old Korean {child_gender} with [KEEP_CONSISTENT_CHARACTER_FEATURES]. [Specific scene description]. Warm pastel colors, soft natural lighting, 2D illustration style, child-friendly background. Character must look identical to previous scenes."
        }}
    ]
}}
"""
        return prompt
    
    async def generate_story_with_gpt4o_mini(self, request: StoryRequest, facial_features: str = None) -> Dict[str, Any]:
        """GPT-4o-mini를 사용한 스토리 생성 (사진 분석 결과 포함)"""
        try:
            print(f"📝 GPT-4o-mini로 스토리 생성 중...")
            
            prompt = self.generate_story_prompt(
                request.child_profile.name,
                request.child_profile.age,
                request.child_profile.gender,
                request.theme,
                facial_features
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
    
    async def generate_image_with_dalle3(self, image_prompt: str, scene_number: int, reference_gen_id: str = None) -> Tuple[str, str]:
        """DALL-E 3를 사용한 이미지 생성 (gen_id 기반 일관성)"""
        try:
            print(f"🎨 DALL-E 3로 장면 {scene_number} 이미지 생성 중...")
            
            # gen_id가 있으면 프롬프트에 포함하여 캐릭터 일관성 유지
            if reference_gen_id:
                image_prompt = f"[Reference generation ID for character consistency: {reference_gen_id}] {image_prompt}"
                print(f"🎯 캐릭터 일관성을 위한 Gen ID 참조: {reference_gen_id}")
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",  # DALL-E 3 최소 지원 해상도
                quality="standard",  # 품질 유지
                n=1
            )
            
            image_url = response.data[0].url
            
            # gen_id 추출 (DALL-E 3 응답에서)
            gen_id = None
            if hasattr(response.data[0], 'revised_prompt'):
                # 실제 API 응답 구조에 따라 조정 필요
                gen_id = getattr(response.data[0], 'gen_id', None) or f"gen_{scene_number}_{hash(image_prompt) % 10000}"
            else:
                # gen_id가 없으면 임시로 생성
                gen_id = f"gen_{scene_number}_{hash(image_prompt) % 10000}"
            
            print(f"✅ 장면 {scene_number} 이미지 생성 완료, Gen ID: {gen_id}")
            return image_url, gen_id
            
        except Exception as e:
            print(f"❌ DALL-E 3 이미지 생성 실패: {str(e)}")
            # 실패시 플레이스홀더 이미지 반환
            placeholder_url = f"https://picsum.photos/1024/1024?random={scene_number}&blur=1"
            return placeholder_url, None
    
    async def generate_scene_with_reference(self, reference_image_url: str, scene_prompt: str, scene_number: int) -> str:
        """Scene 1을 참조하여 다른 장면들을 images.edit API로 생성"""
        try:
            print(f"🎨 장면 {scene_number} 이미지 생성 중 (참조 이미지 기반)...")
            
            # 참조 이미지 다운로드 및 PNG 변환
            import requests
            from PIL import Image
            import io
            
            response = requests.get(reference_image_url)
            if response.status_code != 200:
                raise Exception(f"참조 이미지 다운로드 실패: {reference_image_url}")
            
            # PIL로 이미지를 PNG로 변환
            image = Image.open(io.BytesIO(response.content))
            png_buffer = io.BytesIO()
            image.save(png_buffer, format='PNG')
            png_buffer.seek(0)
            
            # OpenAI images.edit API 호출 (PNG 파일 객체로 전달)
            edit_response = client.images.edit(
                image=png_buffer,
                prompt=f"""Transform this scene while keeping the SAME CHARACTER with identical appearance: {scene_prompt}

IMPORTANT: The main character must look exactly the same as in the reference image:
- Same face, eyes, hair, skin tone
- Same artistic style and proportions  
- Same clothing style
- Only change the background and scene setting
- Maintain soft watercolor children's book illustration style""",
                size="1024x1024"
            )
            
            edited_image_url = edit_response.data[0].url
            print(f"✅ 장면 {scene_number} 이미지 생성 완료 (참조 기반)")
            return edited_image_url
            
        except Exception as e:
            print(f"❌ 장면 {scene_number} 참조 기반 이미지 생성 실패: {str(e)}")
            print(f"🔄 DALL-E 3 직접 생성으로 대체...")
            # 실패시 기본 DALL-E 3로 대체
            return await self.generate_image_with_dalle3(scene_prompt, scene_number)
    
    async def generate_audio_with_tts1(self, text: str, scene_number: int, child_name: str) -> str:
        """OpenAI TTS-1을 사용한 음성 생성"""
        try:
            print(f"🔊 TTS-1로 장면 {scene_number} 음성 생성 중...")
            
            response = client.audio.speech.create(
                model="tts-1",
                voice=settings.TTS_VOICE,  # 설정에서 가져온 목소리
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
    
    async def generate_complete_story(self, request: StoryRequest, facial_features: str = None) -> CompleteStoryResponse:
        """OpenAI 모델들을 사용한 완전한 동화 생성 (사진 분석 결과 포함)"""
        try:
            print(f"🚀 OpenAI 완전 동화 생성 시작: {request.child_profile.name}, 테마: {request.theme}")
            if facial_features:
                print(f"👶 사진 분석 결과 적용: {facial_features[:50]}...")
            
            # 1. GPT-4o로 스토리 생성 (사진 분석 결과 포함)
            story_data = await self.generate_story_with_gpt4o_mini(request, facial_features)
            
            # 2. 상세한 캐릭터 디스크립션 생성
            character_description = self.generate_detailed_character_description(
                request.child_profile.name, 
                request.child_profile.age, 
                request.child_profile.gender,
                facial_features
            )
            
            # 3. Gen ID 기반 캐릭터 일관성 유지 시스템
            scenes = []
            reference_gen_id = None
            
            for i, scene_data in enumerate(story_data.get("scenes", [])[:6]):  # 최대 6개 장면
                scene_num = scene_data.get("scene_number", i + 1)
                scene_text = scene_data.get("text", "")
                base_image_prompt = scene_data.get("image_prompt", f"Children's book illustration, scene {scene_num}")
                
                # 이미지 생성
                if os.getenv("GENERATE_IMAGES", "false").lower() == "true":
                    enhanced_prompt = self.enhance_prompt_for_consistency(
                        base_image_prompt, 
                        character_description, 
                        scene_num
                    )
                    
                    # 2D 동화책 스타일 강조 (3D 방지)
                    enhanced_prompt = f"2D flat illustration, watercolor children's book art style, NOT 3D: {enhanced_prompt}"
                    
                    if scene_num == 1:
                        # Scene 1: 기준 캐릭터 생성 및 gen_id 저장
                        image_url, reference_gen_id = await self.generate_image_with_dalle3(enhanced_prompt, scene_num)
                        print(f"🎯 Scene 1 기준 이미지 생성 완료, Gen ID: {reference_gen_id}")
                    else:
                        # Scene 2-6: gen_id 참조하여 캐릭터 일관성 유지
                        image_url, _ = await self.generate_image_with_dalle3(enhanced_prompt, scene_num, reference_gen_id)
                        print(f"🎨 Scene {scene_num} 이미지 생성 완료 (Gen ID 참조)")
                    
                else:
                    # 플레이스홀더 이미지 사용 (비용 절약)
                    colors = ["8B5CF6", "EC4899", "F59E0B", "10B981", "3B82F6", "8B5A2B"]
                    color = colors[scene_num % len(colors)]
                    image_url = f"https://picsum.photos/1024/1024?random={scene_num}&blur=1"
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
                character_prompt = f"2D flat illustration, watercolor children's book art style, NOT 3D: Children's book character illustration of {request.child_profile.name}, a {request.child_profile.age}-year-old Korean {request.child_profile.gender}, watercolor style, friendly and warm"
                character_image, _ = await self.generate_image_with_dalle3(character_prompt, 0)  # tuple에서 URL만 추출
            else:
                character_image = f"https://picsum.photos/1024/1024?random=character&blur=2"
            
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
