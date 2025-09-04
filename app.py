from flask import Flask, request, render_template_string, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document
import os, uuid

app = Flask(__name__)

# HTML UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PDF Converter</title>
  <style>
    body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
    h1 { color: #333; }
    form { margin: 20px auto; padding: 20px; border: 2px solid #333; border-radius: 12px; max-width: 400px; background: #f9f9f9; }
    input[type=file] { margin: 15px 0; }
    button {
      padding: 10px 20px; border: 2px solid #333; background: white; border-radius: 8px;
      cursor: pointer; font-size: 16px; transition: 0.3s;
    }
    button:hover { background: #333; color: white; }
  </style>
</head>
<body>
  <h1>📄 Free PDF Converter</h1>
  <form method="POST" action="/convert" enctype="multipart/form-data">
    <input type="file" name="file" accept=".docx,.txt" required><br>
    <button type="submit">Convert to PDF</button>
  </form>
</body>
</html>
"""

def txt_to_pdf(input_path, output_path):
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y = height - 50

    for line in lines:
        c.drawString(50, y, line.strip())
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()

def docx_to_pdf(input_path, output_path):
    doc = Document(input_path)
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y = height - 50

    for para in doc.paragraphs:
        text = para.text
        c.drawString(50, y, text)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/convert", methods=["POST"])
def convert():
    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return "❌ No file selected."

    # Temporary save
    input_path = f"/tmp/{uuid.uuid4()}_{uploaded_file.filename}"
    uploaded_file.save(input_path)
    output_path = input_path.rsplit(".", 1)[0] + ".pdf"

    ext = uploaded_file.filename.lower().split(".")[-1]
    try:
        if ext == "txt":
            txt_to_pdf(input_path, output_path)
        elif ext == "docx":
            docx_to_pdf(input_path, output_path)
        else:
            return "❌ Only .txt and .docx supported."
    except Exception as e:
        return f"⚠️ Conversion failed: {str(e)}"

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
