from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import google.generativeai as genai
from PIL import Image
import fitz
import json
import io
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Resume Parser API")

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...), api_key: str = None):
    if not GEMINI_API_KEY and not api_key:
        raise HTTPException(status_code=400, detail="API key required")
    
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    try:
        # Configure API if provided
        if api_key:
            genai.configure(api_key=api_key)
        
        # Read PDF file
        pdf_content = await file.read()
        
        # Convert PDF to images
        pdf = fitz.open(stream=pdf_content, filetype="pdf")
        images = [Image.open(io.BytesIO(page.get_pixmap().tobytes("png"))) for page in pdf]
        pdf.close()
        
        # Send to LLM
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = """Extract resume data as JSON:
{
  "personal_information": {"name": "", "email": "", "phone": "", "linkedin_url": ""},
  "education": [{"institution": "", "degree": "", "dates": ""}],
  "work_experience": [{"company": "", "position": "", "dates": "", "responsibilities": []}],
  "certifications": [{"name": "", "issuing_org": "", "date": ""}],
  "projects": [{"name": "", "description": "", "technologies": []}]
}"""
        
        response = model.generate_content([prompt] + images)
        result = json.loads(response.text.strip('```json').strip('```'))
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Resume Parser API"}
