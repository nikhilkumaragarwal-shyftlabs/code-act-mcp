FROM python:3.11-slim

# Install all allowed libraries
RUN pip install --no-cache-dir \
    pandas numpy openpyxl xlsxwriter PyPDF2 pdfplumber python-docx python-pptx \
    pillow pytesseract matplotlib plotly seaborn reportlab 