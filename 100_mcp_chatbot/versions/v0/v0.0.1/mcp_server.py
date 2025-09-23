import logging
import httpx

logger = logging.getLogger(__name__)

from fastmcp import FastMCP

app = FastMCP(name="LLMExecutorServer") # 앱 이름 변경

# Ollama 서버 URL
OLLAMA_BASE_URL = "http://localhost:11434"

# Ollama 모델 호출 헬퍼 함수
async def _call_ollama_model(model_name: str, prompt: str) -> str:
    async with httpx.AsyncClient(base_url=OLLAMA_BASE_URL) as client:
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7}
        }
        try:
            response = await client.post("/api/generate", json=payload, timeout=300.0)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except httpx.RequestError as e:
            return f"Error connecting to Ollama for {model_name}: {e}"
        except httpx.HTTPStatusError as e:
            return f"Ollama API error for {model_name}: {e.response.text}"
        except Exception as e:
            return f"Unexpected error calling Ollama for {model_name}: {e}"

@app.tool("call_llm_tool") # 범용 LLM 호출 도구
async def call_llm_tool(model_name: str, prompt: str) -> str:
    """Generates a response using a specified Ollama model."""
    logger.info(f"Tool 'call_llm_tool' executed for model: '{model_name}' with prompt: '{prompt}'")
    return await _call_ollama_model(model_name, prompt)

if __name__ == "__main__":
    # Configure logging to show INFO messages from our custom logger
    logging.basicConfig(level=logging.INFO)
    app.run(transport="http", host="0.0.0.0", port=8000)
