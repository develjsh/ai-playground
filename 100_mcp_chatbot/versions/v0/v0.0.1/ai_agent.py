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
    description="Routes queries, handles file uploads, and analyzes PDFs."
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
        user_message = request.msg
        result = await mcp_client.call_tool("call_llm_tool", arguments={"model_name": "deepseek-r1:8b", "prompt": user_message})
        return {"status": "success", "llm_response": result.content}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)