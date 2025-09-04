import cloudconvert
import os
from flask import Flask, request, render_template_string, send_file
import requests

API_KEY = os.getenv("CLOUDCONVERT_API_KEY")
if not API_KEY:
    raise Exception("CLOUDCONVERT_API_KEY not set!")

cloudconvert_api = cloudconvert.Api(api_key=API_KEY)

app = Flask(__name__)

# ... HTML template remains the same ...

@app.route('/convert', methods=['POST'])
def convert_file():
    file = request.files['file']
    if not file.filename.endswith(".docx"):
        return "Please upload a DOCX file only."

    input_path = "input.docx"
    output_path = "output.pdf"
    file.save(input_path)

    job = cloudconvert_api.jobs.create(payload={
        "tasks": {
            "import-1": {"operation": "import/upload"},
            "convert-1": {
                "operation": "convert",
                "input": "import-1",
                "input_format": "docx",
                "output_format": "pdf"
            },
            "export-1": {
                "operation": "export/url",
                "input": "convert-1"
            }
        }
    })

    upload_task = next(task for task in job["tasks"] if task["operation"] == "import/upload")

    cloudconvert_api.tasks.upload(upload_task["id"], input_path)

    job = cloudconvert_api.jobs.wait(job["id"])

    export_task = next(task for task in job["tasks"] if task["operation"] == "export/url")
    file_url = export_task["result"]["files"][0]["url"]

    # Download the file using requests instead of os.system curl
    r = requests.get(file_url)
    with open(output_path, "wb") as f:
        f.write(r.content)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run()
