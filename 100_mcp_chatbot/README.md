# MCP chatbot
Model Context Protocool을 사용하여 보다 쉽게 질문과 상황에 맞게 더 적합한 LLLM을 사용해서 응답하는것이 목표입니다.

## 환경
- Mac m1
- Python 3.10.14

## 설치 라이브러리
*가상환경: python3 -m ven venv


## 기능
1. AI 기반 동적 라우터 (ai_agent.py)

* 사용자의 모든 요청을 받는 기본 진입점(Entry Point) 역할을 합니다.
* 강력한 LLM(gpt-oss:20b)을 '생각하는 두뇌'로 사용하여 사용자의 자연어 질문을 분석하고 의도를 파악합니다.
* 분석 결과를 바탕으로, deepseek-r1:8b(범용 질문용) 또는 mistral:latest(빠른 답변용) 등, 현재 사용 가능한 LLM 중에서 어떤 모델이 해당 요청을 가장 잘 처리할지 동적으로 결정하고 작업을 지시합니다.

2. 범용 LLM 실행기 (mcp_server.py)

* 라우터로부터 지시를 받아 실제 LLM을 호출하는 '실행기(Executor)' 역할을 합니다.
* call_llm_tool이라는 범용 도구를 통해, 지정된 model_name과 prompt를 받아 Ollama 서버에 있는 어떤 모델이든 실행할 수 있습니다.
* 라우터의 결정을 받아 실제 작업을 수행하는 '손과 발'의 역할을 담당합니다.

