# Financial Statement Research Web App

A Streamlit-based web application for extracting and normalizing financial statement line items from PDF documents.

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **OCR**: Tesseract + pdf2image
- **Data Processing**: Pandas, OpenPyXL

## Local Development

### Prerequisites
- Python 3.11+
- Tesseract OCR
- Poppler utils

### Installation

1. Clone the repository:
```bash
git clone https://github.com/cdrocks1117/financial_analysis.git
cd financial_analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler
```

### Running Locally

1. Start the backend:
```bash
python backend.py
```

2. In a new terminal, start Streamlit:
```bash
streamlit run streamlit_app.py
```

3. Open your browser to `http://localhost:8501`

## Deployment

### Streamlit Cloud (Frontend)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set main file to `streamlit_app.py`
5. Add backend URL to secrets

### Render (Backend)
1. Create account at [render.com](https://render.com)
2. Create new Web Service
3. Connect your repository
4. Deploy

## Configuration

Create `.streamlit/secrets.toml`:
```toml
BACKEND_URL = "http://localhost:8000"  # For local development
# BACKEND_URL = "https://your-backend.onrender.com"  # For production
```

## License

MIT
