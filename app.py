from flask import Flask, request, render_template_string, send_file
import cloudconvert
import os
import requests

app = Flask(__name__)

# CloudConvert API Key from environment variable
API_KEY = os.getenv("CLOUDCONVERT_API_KEY")
cloudconvert.configure(api_key=API_KEY)

# HTML Template
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>DOCX to PDF Converter</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; text-align: center; padding: 50px; }
        .box { background: white; padding: 30px; border-radius: 15px; box-shadow: 0px 5px 20px rgba(0,0,0,0.2); display: inline-block; }
        input[type=file] { margin: 20px; }
        button { padding: 10px 20px; border: 2px solid black; border-radius: 10px; background: none; cursor: pointer; transition: 0.3s; }
        button:hover { background: black; color: white; }
    </style>
</head>
<body>
    <div class="box">
        <h2>DOCX → PDF Converter</h2>
        <form method="POST" action="/convert" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <br>
            <button type="submit">Convert</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/convert', methods=['POST'])
def convert_file():
    uploaded_file = request.files['file']
    if not uploaded_file.filename.endswith(".docx"):
        return "Please upload a DOCX file only."

    input_path = "input.docx"
    output_path = "output.pdf"
    uploaded_file.save(input_path)

    # Create CloudConvert Job
    job = cloudconvert.Job.create(payload={
        "tasks": {
            "import-my-file": {
                "operation": "import/upload"
            },
            "convert-my-file": {
                "operation": "convert",
                "input": "import-my-file",
                "input_format": "docx",
                "output_format": "pdf",
            },
            "export-my-file": {
                "operation": "export/url",
                "input": "convert-my-file"
            }
        }
    })

    # Upload DOCX file
    upload_task = job["tasks"][0]
    cloudconvert.Task.upload(upload_task, input_path)

    # Wait for job to complete
    job = cloudconvert.Job.wait(job["id"])
    export_task = [t for t in job["tasks"] if t["name"] == "export-my-file"][0]
    file_url = export_task["result"]["files"][0]["url"]

    # Download the PDF
    r = requests.get(file_url)
    with open(output_path, 'wb') as f:
        f.write(r.content)

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
