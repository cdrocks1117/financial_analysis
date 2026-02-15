from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO
from pdf2image import convert_from_bytes
import pytesseract
import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Financial Statement Extractor API")

# CORS Configuration - Update this with your Vercel domain
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    # Add your Vercel domain here after deployment
    # "https://your-app.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if Tesseract is available
try:
    pytesseract.get_tesseract_version()
    logger.info("Tesseract is available")
except Exception as e:
    logger.warning(f"Tesseract not found: {e}")

def parse_financial_lines(text_data):
    """
    Parse OCR text into structured financial line items
    Returns a list of dictionaries with line_item and value
    """
    lines = text_data.strip().split('\n')
    parsed_data = []
    
    # Pattern to match financial line items (text followed by numbers)
    pattern = re.compile(r'^([A-Za-z\s\(\)&,.-]+?)\s*[:|\s]\s*([-]?\$?\s*[\d,]+\.?\d*)\s*$')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = pattern.match(line)
        if match:
            line_item = match.group(1).strip()
            value = match.group(2).strip().replace('$', '').replace(',', '')
            parsed_data.append({
                'Line Item': line_item,
                'Value': value
            })
        else:
            # If line doesn't match pattern, try to extract any numbers
            numbers = re.findall(r'[-]?\$?\s*[\d,]+\.?\d*', line)
            if numbers and len(line) > 3:
                label = re.sub(r'[-]?\$?\s*[\d,]+\.?\d*', '', line).strip()
                if label:
                    value = numbers[0].strip().replace('$', '').replace(',', '')
                    parsed_data.append({
                        'Line Item': label,
                        'Value': value
                    })
    
    return parsed_data

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Financial Statement Extractor API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    tesseract_available = False
    try:
        pytesseract.get_tesseract_version()
        tesseract_available = True
    except:
        pass
    
    return {
        "status": "healthy",
        "tesseract_available": tesseract_available,
        "poppler_configured": os.environ.get("POPPLER_PATH") is not None
    }

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Process uploaded PDF and return Excel file with extracted financial data
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        logger.info(f"Processing file: {file.filename}")
        
        # Read file contents
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        logger.info(f"File size: {len(contents)} bytes")
        
        # Convert PDF to images
        try:
            # Poppler path will be set via environment variable in Render
            poppler_path = os.environ.get("POPPLER_PATH")
            
            if poppler_path:
                images = convert_from_bytes(contents, poppler_path=poppler_path)
            else:
                images = convert_from_bytes(contents)
            
            logger.info(f"Converted PDF to {len(images)} images")
        except Exception as e:
            logger.error(f"PDF conversion error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to convert PDF: {str(e)}")
        
        # Extract text using OCR
        text_data = ""
        for i, img in enumerate(images):
            try:
                page_text = pytesseract.image_to_string(img)
                text_data += page_text
                logger.info(f"Processed page {i+1}/{len(images)}")
            except Exception as e:
                logger.error(f"OCR error on page {i+1}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"OCR failed on page {i+1}: {str(e)}")
        
        if not text_data.strip():
            text_data = "No text detected via OCR."
            df = pd.DataFrame({"Message": [text_data]})
        else:
            # Parse the extracted text into structured data
            parsed_data = parse_financial_lines(text_data)
            
            if parsed_data:
                df = pd.DataFrame(parsed_data)
            else:
                # Fallback: split by lines if parsing fails
                lines = [line.strip() for line in text_data.split('\n') if line.strip()]
                df = pd.DataFrame({"Extracted Text": lines})
        
        logger.info(f"Created DataFrame with {len(df)} rows")
        
        # Create Excel file
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Financial Data')
            
            # Get the worksheet
            worksheet = writer.sheets['Financial Data']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        logger.info("Successfully created Excel file")
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=Financial_Output.xlsx"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)