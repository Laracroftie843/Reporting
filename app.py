from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
from report_and_email import create_pdf_report
import glob

app = Flask(__name__)
UPLOAD_FOLDER = "csvs"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    # Serve frontend (if you prefer HTML file, see below)
    return send_from_directory("frontend", "index.html")

@app.route("/upload", methods=["POST"])
def upload_files():
    if "files[]" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files[]")
    saved_files = []

    for file in files:
        if file.filename == "":
            continue
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        saved_files.append(path)

    if not saved_files:
        return jsonify({"error": "No valid files uploaded"}), 400

    # Generate combined report
    pdf_output = os.path.join(OUTPUT_FOLDER, "weekly_report.pdf")
    create_pdf_report(saved_files, column_map={f: None for f in saved_files}, output_file=pdf_output)

    return jsonify({
        "message": "Report generated successfully!",
        "pdf_download": "/download/weekly_report.pdf"
    })

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

