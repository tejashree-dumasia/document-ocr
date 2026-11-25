import os
import cv2
import numpy as np
import easyocr
import json
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("API_KEY not found in .env file")

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- INITIALIZE API & MODELS ---
app = FastAPI(title="Dynamic Document OCR API")
client = genai.Client(api_key=api_key)

# Load EasyOCR into memory once when the server starts
logger.info("Loading EasyOCR Model into memory...")
reader = easyocr.Reader(['en'])

def preprocess_image(image_bytes):
    """Processes the image entirely in memory without saving to disk."""
    logger.info("[1/3] Preprocessing uploaded image...")
    # Convert uploaded byte stream into a numpy array for OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return processed

# --- RETRY LOGIC ---
# If Gemini throws a 503, wait 2 seconds, then try again (up to 3 times)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def parse_with_gemini(raw_text, target_schema):
    logger.info("[3/3] Sending to Gemini API with automatic retries...")
    prompt = f"""
    Extract data from this OCR text based on the provided Target Schema.
    Return ONLY a valid JSON object matching the requested keys. 
    If a requested field is not found in the text, return null for that field.
    
    Target Schema format requested by user:
    {target_schema}
    
    Raw Text:
    {raw_text}
    """
    
    response = client.models.generate_content(
        model='gemini-3.8-flash', 
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return response.text

# --- API ENDPOINT ---
@app.post("/api/v1/extract")
async def extract_document(
    file: UploadFile = File(...), 
    schema_definition: str = Form(...)
):
    try:
        # Validate that the user sent a proper JSON string for the schema
        try:
            json.loads(schema_definition)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="schema_definition must be a valid JSON string.")

        image_bytes = await file.read()
        
        # Step 1: Preprocess in-memory
        clean_image = preprocess_image(image_bytes)
        
        # Step 2: OCR Extraction
        logger.info("[2/3] Extracting text with EasyOCR...")
        # EasyOCR can read numpy arrays directly, no need to save to disk!
        lines = reader.readtext(clean_image, detail=0)
        raw_text = "\n".join(lines)
        
        # Step 3: AI Parsing
        json_data = parse_with_gemini(raw_text, schema_definition)
        
        logger.info("Extraction successful! Returning data to client.")
        return json.loads(json_data)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error during processing.")