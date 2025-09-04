from flask import Flask, request, send_file, render_template_string
from docx2pdf import convert
from PIL import Image
import os
import pythoncom   # Fix for CoInitialize error

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- DOCX → PDF using MS Word ---
def convert_docx_to_pdf(file):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    file.save(filepath)

    # Fix COM threading issue in Flask
    pythoncom.CoInitialize()
    convert(filepath)   # DOCX → PDF
    pythoncom.CoUninitialize()

    output_path = filepath.replace(".docx", ".pdf")
    return output_path

# --- Images → PDF ---
def convert_images_to_pdf(files):
    imgs = []
    for f in files:
        path = os.path.join(UPLOAD_DIR, f.filename)
        f.save(path)
        img = Image.open(path).convert("RGB")
        imgs.append(img)
    output_path = os.path.join(UPLOAD_DIR, "output.pdf")
    imgs[0].save(output_path, save_all=True, append_images=imgs[1:])
    return output_path

# --- Stylish HTML (UI) ---
HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>File Converter</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh; 
      display: flex; 
      align-items: center; 
      justify-content: center; 
    }
    .card { 
      border-radius: 20px; 
      box-shadow: 0px 8px 25px rgba(0,0,0,0.2); 
      background: white; 
      padding: 30px; 
      max-width: 500px;
      margin: auto;
    }
    .btn-custom { 
      background: #667eea; 
      color: white; 
      border-radius: 12px; 
      transition: 0.3s; 
    }
    .btn-custom:hover { 
      background: #5a67d8; 
      transform: scale(1.05); 
    }
    h1 { 
      color: #4e73df; 
      font-weight: bold; 
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1 class="text-center mb-4">📄 File to PDF Converter</h1>
      <form method="post" enctype="multipart/form-data">
        <div class="mb-3">
          <label class="form-label fw-bold">Choose Conversion Type</label><br>
          <input type="radio" name="choice" value="docx" required> DOCX → PDF <br>
          <input type="radio" name="choice" value="img" required> Images → PDF
        </div>
        <div class="mb-3">
          <label class="form-label fw-bold">Upload Files</label>
          <input type="file" class="form-control" name="file" multiple required>
        </div>
        <button type="submit" class="btn btn-custom w-100">Convert 🚀</button>
      </form>
    </div>
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template_string(HTML)
    
    choice = request.form.get("choice")
    files = request.files.getlist("file")

    if choice == "docx" and len(files) == 1 and files[0].filename.lower().endswith(".docx"):
        out = convert_docx_to_pdf(files[0])
    elif choice == "img" and all(f.filename.lower().endswith((".jpg",".jpeg",".png")) for f in files):
        out = convert_images_to_pdf(files)
    else:
        return "<h2 style='color:red;text-align:center;'>❌ Invalid selection or files</h2>"

    return send_file(out, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
