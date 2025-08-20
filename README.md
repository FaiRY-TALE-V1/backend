# 🧚‍♀️ FaiRY TALE 백엔드 서버

Qwen-Image-Edit 모델을 사용한 AI 이미지 편집 기능이 포함된 FastAPI 백엔드 서버입니다.

## 🚀 빠른 시작

### 1. Conda 환경 설정 (권장)

```bash
# 백엔드 디렉토리로 이동
cd backend

# Conda 환경 자동 설정 (Apple Silicon 최적화 포함)
./setup_conda_env.sh

# 환경 활성화
conda activate fairytale-backend
```

### 2. 수동 설치 (선택사항)

```bash
# 환경 변수 파일 생성
cp env_setup.txt .env
# .env 파일을 편집하여 실제 API 키를 입력하세요

# Python 패키지 설치
pip install -r requirements.txt
```

### 3. 서버 실행

#### 방법 1: 자동 스크립트 사용 (권장)

```bash
python start_server.py
```

#### 방법 2: 수동 실행

```bash
python main.py
# 또는
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🎯 API 엔드포인트

### 기본 엔드포인트

- `GET /` - API 상태 확인
- `GET /themes` - 사용 가능한 테마 목록
- `POST /generate_complete_story` - 통합 스토리 생성

### Qwen-Image-Edit 엔드포인트

- `POST /qwen/generate-character` - 아이 사진을 동화 캐릭터로 변환
- `POST /qwen/generate-scene` - 개인화된 동화 장면 생성
- `POST /qwen/add-text` - 이미지에 텍스트 추가
- `POST /qwen/custom-edit` - 사용자 정의 이미지 편집
- `GET /qwen/status` - Qwen 모델 상태 확인

## 🖥️ 시스템 요구사항

### 최소 사양

- **Python**: 3.8 이상
- **RAM**: 8GB 이상
- **디스크**: 10GB 여유 공간 (모델 다운로드용)

### 권장 사양 (GPU 사용)

- **GPU**: NVIDIA GPU (8GB VRAM 이상)
- **CUDA**: 11.8 이상
- **RAM**: 16GB 이상

### CPU 전용 실행

- GPU가 없어도 CPU 모드로 실행 가능합니다
- 처리 속도가 느려질 수 있습니다 (이미지당 1-3분)

## 🔧 환경 변수

`.env` 파일에 다음 변수들을 설정하세요:

```env
# OpenAI API (기존 스토리 생성용)
OPENAI_API_KEY=your_openai_api_key_here

# 서버 설정
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Qwen 모델 설정
QWEN_MODEL_CACHE_DIR=./model_cache
QWEN_MAX_MEMORY_GB=8

# MPS 설정 (Apple Silicon)
MPS_FALLBACK=True
```

## 📊 모델 정보

### Qwen-Image-Edit

- **모델**: Alibaba의 Qwen-Image-Edit
- **용도**: 이미지 편집 및 개인화
- **특징**:
  - 시맨틱 편집과 외관 편집 지원
  - 한국어/영어 텍스트 편집 가능
  - 캐릭터 일관성 유지

### 첫 실행 시 주의사항

- 모델이 자동으로 다운로드됩니다 (약 20GB)
- 인터넷 연결이 필요합니다
- 초기 로딩에 5-10분 소요될 수 있습니다

## 🐛 문제 해결

### 일반적인 오류

#### 1. CUDA 메모리 부족

```
RuntimeError: CUDA out of memory
```

**해결책**: `.env`에서 `CUDA_AVAILABLE=False`로 설정

#### 2. 모델 다운로드 실패

```
Connection error
```

**해결책**:

- 인터넷 연결 확인
- VPN 사용 시 해제 후 재시도
- `rm -rf model_cache/` 후 재시작

#### 3. 포트 충돌

```
Address already in use
```

**해결책**: `.env`에서 `PORT=8001`로 변경

### 로그 확인

서버 실행 시 콘솔에서 다음과 같은 로그를 확인하세요:

```
✅ Qwen-Image-Edit 모델이 성공적으로 로드되었습니다.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 🔗 프론트엔드 연동

프론트엔드가 다음 주소로 API를 호출합니다:

- 개발 환경: `http://localhost:8000`
- CORS가 `http://localhost:3000`을 허용하도록 설정됨

## 📈 성능 최적화

### GPU 사용 시

- 이미지 편집: 15-30초
- 메모리 사용량: 6-8GB

### CPU 사용 시

- 이미지 편집: 1-3분
- 메모리 사용량: 4-6GB

## 🆘 지원

문제가 발생하면 다음을 확인하세요:

1. **모델 상태**: `GET /qwen/status`
2. **로그 파일**: 콘솔 출력 확인
3. **디스크 공간**: 모델 다운로드용 여유 공간
4. **네트워크**: Hugging Face 접속 가능 여부
