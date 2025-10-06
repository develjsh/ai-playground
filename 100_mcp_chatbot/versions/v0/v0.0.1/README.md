# MCP chatbot


## 환경
- Mac m1
- Python 3.10.14

## 설치 방법 (Installation)

### 1. Python 가상환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 시스템 의존성 설치 (macOS with Homebrew)
PDF 분석 및 OCR 기능에 필요한 핵심 엔진들을 설치합니다.
```bash
brew install libmagic tesseract poppler
```

### 3. Python 라이브러리 설치
프로젝트 실행에 필요한 모든 Python 라이브러리를 설치합니다.
```bash
pip install fastapi uvicorn fastmcp transformers torch requests python-magic Pillow pytesseract PyMuPDF
```

## 지원 LLM model
NAME              ID              SIZE
deepseek-r1:8b    6995872bfe4c    5.2 GB
gpt-oss:20b       aa4295ac10c3    13 GB
mistral:latest    6577803aa9a0    4.4 GB
