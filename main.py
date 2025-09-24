import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import io
import os
import google.generativeai as genai

# Load .env
load_dotenv()

# Get API key
API_KEY = os.getenv("GOOGLE_API_KEY")   # 👈 must match .env variable

if not API_KEY:
    st.error("❌ API Key not found. Please set GOOGLE_API_KEY in .env file")
else:
    genai.configure(api_key=API_KEY)

# ~~~~~~~~~~~~~~~ setup ui ~~~~~~~~~~~~~~~~~~~
st.title("Resume Parsing")
st.warning("This is a demo app. Please do not upload sensitive documents.")

# Sidebar for manual API key (optional override)
manual_key = st.sidebar.text_input("Enter your API key", type="password")
if manual_key:
    genai.configure(api_key=manual_key)

# File upload (PDF only)
upload_file = st.file_uploader(
    "Upload your resume PDF only", 
    type=["pdf"], 
    key="resume_uploader"
)

if upload_file is not None:
    pdf_file = io.BytesIO(upload_file.read())
    pdf_reader = PdfReader(pdf_file)

    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()

    if extracted_text:
        st.write("✅ Text extracted from PDF successfully.")

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        Extract the following sections from the provided resume text and output in JSON format only:
        - personal_information: {{name, email, phone, LinkedIn URL}}
        - education: list of {{institutions, degrees, dates}}
        - work_experience: list of {{companies, positions, dates, responsibilities}}
        - certifications: list of {{certs, issuing org, date}}
        - projects: list of {{project names, descriptions, technologies}}
        
        Resume text: {extracted_text}
        """

        response = model.generate_content(prompt)

        if response.text:
            st.subheader("Extracted Resume Information (JSON format):")
            st.code(response.text, language='json')
else:
    st.info("Please upload a PDF file to continue.")
