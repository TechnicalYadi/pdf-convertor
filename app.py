from flask import Flask, request, render_template_string, send_file
import pypandoc
import os
import uuid

app = Flask(__name__)

# HTML Template (Responsive, Mobile Friendly)
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

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/convert", methods=["POST"])
def convert():
    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return "❌ No file selected."

    # Save uploaded file temporarily
    input_path = f"/tmp/{uuid.uuid4()}_{uploaded_file.filename}"
    uploaded_file.save(input_path)

    # Output file path
    output_path = input_path.rsplit(".", 1)[0] + ".pdf"

    try:
        # Convert DOCX/TXT to PDF
        pypandoc.convert_file(input_path, "pdf", outputfile=output_path)
    except Exception as e:
        return f"⚠️ Conversion failed: {str(e)}"

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
