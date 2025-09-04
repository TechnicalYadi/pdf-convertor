import os
import requests
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

# Apni API Key yaha daalo
API_KEY = "eyJ0eXAiOiJK...v4q4UM"   # 👈 yaha apna pura token paste karo

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    file = request.files['file']
    
    # CloudConvert API upload request
    upload_task = requests.post(
        'https://api.cloudconvert.com/v2/import/upload',
        headers={"Authorization": f"Bearer {API_KEY}"}
    ).json()

    upload_url = upload_task['data']['result']['form']['url']
    form_data = upload_task['data']['result']['form']['parameters']

    files = {'file': (file.filename, file.stream, file.mimetype)}

    # File upload
    requests.post(upload_url, data=form_data, files=files)

    # Conversion task
    convert_task = requests.post(
        'https://api.cloudconvert.com/v2/convert',
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "input": "upload",
            "file": upload_task['data']['id'],
            "output_format": "pdf"   # 👈 yaha tum format change kar sakte ho
        }
    ).json()

    # Download link
    file_url = convert_task['data']['result']['files'][0]['url']
    return f"Converted File: <a href='{file_url}'>Download Here</a>"

if __name__ == "__main__":
    app.run(debug=True)
