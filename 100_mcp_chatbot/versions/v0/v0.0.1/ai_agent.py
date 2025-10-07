from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastmcp.client import Client
import uvicorn
import anyio
import json
import httpx
import magic
import shutil
import os
import uuid
import io

# PDF & Image Analysis Imports
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

# --- App Initialization ---
app = FastAPI(
    title="AI Agent LLM Router",
    description="Routes natural language queries to appropriate LLMs via FastMCP."
)

# --- Mount Static Directory ---
STATIC_DIR = "static"
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount(f"/{STATIC_DIR}", StaticFiles(directory=STATIC_DIR), name="static")

# --- Pydantic Models ---
class NaturalLanguageRequest(BaseModel):
    msg: str

# --- Global instances ---
olama_client: httpx.AsyncClient = None
mcp_client: Client = None
OLLAMA_ROUTER_MODEL_NAME = "gpt-oss:20b"

# --- PDF Analysis Function ---
def analyze_pdf(file_path: str) -> str:
    """Analyzes all pages of a PDF file using PyMuPDF and Tesseract OCR."""
    extracted_text = ""
    try:
        doc = fitz.open(file_path)
        
        # Loop through all pages in the document
        for page_num, page in enumerate(doc):
            extracted_text += f"\n=============== Page {page_num + 1} ===============\n"
            
            # 1. Extract plain text
            text = page.get_text()
            if text.strip():
                extracted_text += f"--- Text ---\n{text}\n"

            # 2. Extract text from images (OCR)
            image_list = page.get_images(full=True)
            if image_list:
                extracted_text += "\n--- OCR Text from Images ---\n"
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    pil_image = Image.open(io.BytesIO(image_bytes))
                    
                    ocr_text = pytesseract.image_to_string(pil_image, lang='eng+kor')
                    if ocr_text.strip():
                        extracted_text += f"[Image {img_index+1} Text]:\n{ocr_text}\n"

        doc.close()
        return extracted_text if extracted_text else "No text or images found in the document."

    except Exception as e:
        return f"Failed to analyze PDF with PyMuPDF. Error: {e}"

# --- Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    global ollama_client, mcp_client
    # httpx 설치 확인
    try:
        import httpx
    except ImportError:
        print("Error: httpx library not found. Please install it using 'pip install httpx'")
        raise

    print("Initializing Ollama HTTP client...")
    ollama_client = httpx.AsyncClient(base_url="http://localhost:11434")
    print("Initializing FastMCP client...")
    mcp_client = Client("http://localhost:8000/mcp")
    await mcp_client.__aenter__()

@app.on_event("shutdown")
async def shutdown_event():
    global ollama_client, mcp_client
    if mcp_client: await mcp_client.__aexit__(None, None, None)
    if ollama_client: await ollama_client.aclose()

# --- API Endpoints ---
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1]
        safe_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        mime_type = magic.from_file(file_path, mime=True)
        print(f"File '{original_filename}' saved as '{safe_filename}'. MIME: {mime_type}")

        response_data = {
            "original_filename": original_filename,
            "content_type": mime_type,
        }

        if mime_type == "application/pdf":
            analysis_result = analyze_pdf(file_path)
            response_data["info"] = analysis_result
        elif mime_type.startswith("image/"):
            response_data["file_url"] = f"http://localhost:8001/{file_path}"
        else:
            response_data["info"] = f"File '{original_filename}' received."

        return response_data

    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
- mistral:latest: A fast and efficient model. Use this for quick, concise answers.
- gpt-oss:20b: (This is me, the router. You can ask me to answer directly too.)

To get a response from a specific LLM, you must specify which model to use.
Example: "mistral:latest 모델로 '프랑스 파리'에 대해 설명해줘."

Respond with a JSON object in the format: {{"tool_name": "call_llm_tool", "tool_args": {{"model_name": "...", "prompt": "..."}}}}
If no specific LLM is requested or you want me (gpt-oss:20b) to answer directly, use {{"tool_name": "none", "response": "..."}}.
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
            return {
                "status": "success",
                "llm_model_used": OLLAMA_ROUTER_MODEL_NAME,
                "llm_response": direct_response
            }
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
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)