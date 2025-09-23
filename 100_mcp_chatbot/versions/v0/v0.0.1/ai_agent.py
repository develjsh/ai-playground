from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastmcp.client import Client
import uvicorn
import anyio
import json
import httpx # Ollama API 호출을 위한 비동기 HTTP 클라이언트

app = FastAPI(
    title="AI Agent LLM Router", # 앱 이름 변경
    description="Routes natural language queries to appropriate LLMs via FastMCP."
)

class NaturalLanguageRequest(BaseModel):
    msg: str

# Global instances
ollama_client: httpx.AsyncClient = None # Ollama HTTP 클라이언트
mcp_client: Client = None
OLLAMA_ROUTER_MODEL_NAME = "gpt-oss 20b" # 라우터 역할을 할 Ollama 모델 이름

@app.on_event("startup")
async def startup_event():
    global ollama_client, mcp_client

    # httpx 설치 확인
    try:
        import httpx
    except ImportError:
        print("Error: httpx library not found. Please install it using 'pip install httpx'")
        raise

    # Ollama HTTP 클라이언트 초기화
    print("Initializing Ollama HTTP client...")
    ollama_client = httpx.AsyncClient(base_url="http://localhost:11434") # Ollama 기본 포트
    print("Ollama HTTP client initialized.")

    # FastMCP 클라이언트 초기화
    mcp_client = Client("http://localhost:8000/mcp")
    await mcp_client.__aenter__()

@app.on_event("shutdown")
async def shutdown_event():
    global ollama_client, mcp_client
    if mcp_client:
        await mcp_client.__aexit__(None, None, None)
    if ollama_client:
        await ollama_client.aclose() # httpx 클라이언트 연결 해제

@app.post("/chat")
async def chat_web(request: NaturalLanguageRequest):
    try:
        if not ollama_client:
            raise HTTPException(status_code=500, detail="Ollama client not initialized.")
        if not mcp_client:
            raise HTTPException(status_code=500, detail="FastMCP client not initialized.")

        user_message = request.msg
        print(f"Received natural language message: '{user_message}'")

        # Ollama에게 제공할 도구 설명 (이제 LLM 모델들이 도구입니다)
        tool_descriptions = f"""
You are an AI assistant that can route user queries to different LLM models.
Available LLM models:
- llama3: A powerful general-purpose model. Use this for general questions.
- mistral: A fast and efficient model. Use this for quick, concise answers.
- gpt-oss 20b: (This is me, the router. You can ask me to answer directly too.)

To get a response from a specific LLM, you must specify which model to use.
Example: "llama3 모델을 사용해서 '인공지능이란 무엇인가?'에 대해 설명해줘."
Example: "mistral 모델로 '프랑스 파리'에 대해 설명해줘."

Respond with a JSON object in the format: {{"tool_name": "call_llm_tool", "tool_args": {{"model_name": "...", "prompt": "..."}}}}
If no specific LLM is requested or you want me (gpt-oss 20b) to answer directly, use {{"tool_name": "none", "response": "..."}}.
Ensure your response is a valid JSON string.
"""

        # Ollama에게 도구 선택을 지시하는 프롬프트 구성
        ollama_prompt = f"""
{tool_descriptions}

User message: {user_message}
"""

        # Ollama (라우터 모델) 호출
        ollama_request_payload = {
            "model": OLLAMA_ROUTER_MODEL_NAME,
            "prompt": ollama_prompt,
            "stream": False,
            "options": {
                "temperature": 0.0 # 라우팅 판단의 일관성을 위해 temperature를 낮춤
            }
        }

        print(f"Calling Ollama API for router model: {OLLAMA_ROUTER_MODEL_NAME}...")
        ollama_response = await ollama_client.post("/api/generate", json=ollama_request_payload, timeout=300.0) # 타임아웃 증가
        ollama_response.raise_for_status() # HTTP 오류 발생 시 예외 발생

        ollama_response_data = ollama_response.json()
        llm_generated_text = ollama_response_data.get("response", "").strip()

        print(f"Ollama raw response: {llm_generated_text}")

        # Ollama 응답에서 도구 선택을 위한 JSON 파싱
        try:
            json_start = llm_generated_text.find('{')
            json_end = llm_generated_text.rfind('}')
            if json_start != -1 and json_end != -1 and json_end > json_start:
                llm_generated_json_str = llm_generated_text[json_start : json_end + 1]
            else:
                llm_generated_json_str = llm_generated_text # JSON이 명확하지 않으면 전체 텍스트 사용

            llm_decision = json.loads(llm_generated_json_str)
            tool_name = llm_decision.get("tool_name")
            tool_args = llm_decision.get("tool_args", {})
            direct_response = llm_decision.get("response")
        except json.JSONDecodeError:
            print(f"Ollama response not valid JSON: {llm_generated_json_str}")
            tool_name = "none"
            direct_response = f"Ollama did not return valid JSON. Raw response: {llm_generated_json_str}"

        if tool_name == "none":
            return {"status": "success", "response": direct_response}
        elif tool_name == "call_llm_tool": # 이제 mcp_server는 이 도구만 가집니다.
            model_to_call = tool_args.get("model_name")
            prompt_for_llm = tool_args.get("prompt")

            if not model_to_call or not prompt_for_llm:
                raise HTTPException(status_code=400, detail="Invalid arguments for call_llm_tool. 'model_name' and 'prompt' are required.")

            print(f"Router decided to call LLM: {model_to_call} with prompt: '{prompt_for_llm}'")

            # mcp_server.py의 범용 LLM 도구 호출
            result = await mcp_client.call_tool("call_llm_tool", arguments={"model_name": model_to_call, "prompt": prompt_for_llm})

            return {
                "status": "success",
                "llm_model_used": model_to_call,
                "prompt_sent": prompt_for_llm,
                "llm_response": result.content
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unexpected tool_name from router: {tool_name}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
