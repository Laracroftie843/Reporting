from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import subprocess
from report_and_email import create_pdf_report
import glob

app = Flask(__name__)
UPLOAD_FOLDER = "csvs"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    # Serve frontend
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

    # Commit and push CSV files to GitHub
    try:
        print("Current working directory:", os.getcwd())
        subprocess.run(["git", "config", "--global", "user.name", "render-bot"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "render@render.com"], check=True)
        
        # Add the saved CSVs
        subprocess.run(["git", "add", "Reporting/csvs"], check=True)

        # Commit changes if there are any
        commit_result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], check=False
        )
        if commit_result.returncode != 0:  # means there ARE staged changes
            subprocess.run(
                ["git", "commit", "-m", "Add new CSV files via web upload"],
                check=True
            )
            # Use token authentication for push (safer than embedding token directly in URL logs)
            repo_url = "https://github.com/Laracroftie843/Reporting.git"
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                return jsonify({"error": "Missing GITHUB_TOKEN in environment"}), 500

            subprocess.run(
                ["git", "push", f"https://{token}:x-oauth-basic@github.com/Laracroftie843/Reporting.git", "report-project"],
                check=True
            )
        else:
            print("No new changes to commit.")
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Git push failed: {e}"}), 500

    # Generate combined PDF report (keeps existing functionality)
    pdf_output = os.path.join(OUTPUT_FOLDER, "weekly_report.pdf")
    create_pdf_report(saved_files, column_map={f: None for f in saved_files}, output_file=pdf_output)

    return jsonify({
        "message": "Report generated and committed successfully!",
        "pdf_download": "/download/weekly_report.pdf"
    })

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
