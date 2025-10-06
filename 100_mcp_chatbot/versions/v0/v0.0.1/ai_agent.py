
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

# --- App Initialization ---
app = FastAPI(
    title="AI Agent LLM Router",
    description="Routes natural language queries and handles file uploads."
)

# --- Mount Static Directory ---
# This makes the 'static' folder publicly accessible to serve images
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

# --- Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    global ollama_client, mcp_client
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
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        # Save the uploaded file to the static directory
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Identify the file type
        mime_type = magic.from_file(file_path, mime=True)
        print(f"File '{file.filename}' uploaded. Detected MIME type: {mime_type}")

        response_data = {
            "filename": file.filename,
            "content_type": mime_type,
        }

        if mime_type.startswith("image/"):
            # If it's an image, return its accessible URL
            # NOTE: Replace 'localhost' with your machine's actual IP address 
            # if you are running the app on a physical device.
            response_data["file_url"] = f"http://localhost:8001/{STATIC_DIR}/uploads/{file.filename}"
        else:
            # For other file types, return a descriptive text
            response_data["info"] = f"File '{file.filename}' received and identified as {mime_type}."

        return response_data

    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the file: {e}")

@app.post("/chat")
async def chat_web(request: NaturalLanguageRequest):
    try:
        user_message = request.msg
        result = await mcp_client.call_tool("call_llm_tool", arguments={"model_name": "deepseek-r1:8b", "prompt": user_message})
        return {
            "status": "success",
            "llm_response": result.content
        }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
