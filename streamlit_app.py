# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="Financial Statement Research",
    page_icon="💰",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 2rem;
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("💰 Financial Statement Research")
st.markdown("---")

# Backend URL configuration
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

# File uploader
uploaded_file = st.file_uploader(
    "Upload PDF Financial Statement",
    type=['pdf'],
    help="Select a PDF file containing financial statements"
)

# Process button
if uploaded_file is not None:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Process Financial Statement", use_container_width=True):
            with st.spinner("Processing PDF... This may take a moment."):
                try:
                    # Prepare the file for upload
                    files = {
                        'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')
                    }
                    
                    # Send request to backend
                    response = requests.post(
                        f"{BACKEND_URL}/upload",
                        files=files,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ Excel file generated successfully!")
                        
                        # Create download button
                        st.download_button(
                            label="📥 Download Excel File",
                            data=response.content,
                            file_name="Financial_Output.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        
                        # Optional: Display preview of the data
                        with st.expander("📊 Preview Data"):
                            try:
                                df = pd.read_excel(BytesIO(response.content))
                                st.dataframe(df, use_container_width=True)
                            except Exception as e:
                                st.info("Preview not available")
                    else:
                        st.error(f"❌ Error: {response.status_code} - {response.text}")
                        
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. The file may be too large or the server is slow.")
                except requests.exceptions.ConnectionError:
                    st.error(f"🔌 Cannot connect to backend at {BACKEND_URL}. Please check if the backend is running.")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

else:
    st.info("👆 Please upload a PDF file to begin processing")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #64748b;'>
        <p>Financial Statement Extractor | Powered by Streamlit & FastAPI</p>
    </div>
    """, unsafe_allow_html=True)
