"""
Iteraton 1:
- Read up to 4 CSVs from 'csvs/' folder
- Keep all columns (editing later)
- Create a single PDF with one labeled section per CSV file
- Send the PDF via SMTP ?Have to figure out if we want this?
"""

import os
import glob
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

# ReportLab
from reportlab.platypus import SimpleDocTemplate, Table, Tablestyle, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSamleStyleSheet
from reportlab.lib import colors

#Email
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

#Read CSV (includes all columns at the moment)
def read_and_scrub_csv(file_path: str, columns_to_keep: Optional[List[str]] = None) -> pd.DataFrame:
  df = pd.read_csv(file_path, dtype=str) #reads as strings
  if columns_to_keep is None:
    return df
  available = [c for c in columns_to_keep if c in df.columns]
  missing = [c for c in columns_to_keep f c not in df.columns]
  if missing:
    print(f"[WARN] Missing columns in {file_path}: {missing}")
  return df[available].copy()

# Converts df -> to reportlab Table
def df_to_reportlab_table(df: pd.DataFrame, style, doc_width) -> Table:
  if df.shape[1] == 0:
    data = [[Paragraph(",i>No columns selected / no data</i>", styles['BodyText'])]]
    return Table(data, colWidths=[doc_width * 0.8])
  header = [Paragraph(str(h), styles['Heading5']) for h in df.columns.tolist()]
  rows = []
  for _, r in df.iterrows():
    rows.append([Paragraph(str(cell), styles['BodyText']) for cell in r.tolist()])
  data = [header] + rows
  #Columns
  col_count = max(1, df.shape[1])
  min_col_w = 50
  proposed = doc_width / col_count
  col_widths = [proposed] * col_count if proposed >= min_col_w else [min_col_] * col_count
  # Table
  tbl = Table(data, colWidths=col_widths, repeatRows=1)
  tbl.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#4F81BD")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("BOTTOMPADDING", (0,0), (-1,0), 6),
    ("GRID", (0,0), (-1,-1), 0.25, colors.black),
  ]))
  return tbl

#Creates PDF Report
def create_pdf_reort(csv_files: List[str}, column_map: Dict[str, Optional[List[str]}}, output_file: str = "weekly_report.pdf") -> str:
  doc = SimpleDocTemplate(output_file, pagesize=LETTER, leftMargin=36, rightMargin=36,topMargin=36, bottomMargin=36)
  styles = getSampleStyleSheet()
  story = []

  page_width = LETTER[0]
  available_with = page_width - doc.lefftMargin - doc.rightMargin

  generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  story.append(Paragraph(f"Combined Weekly Report (generated [generated_time})", styles['Title']))
  story.append (Spacer(1,12))

  for idx, file_path in enumerate(csv_files, start=1):
    basename = os.path.basename(file_path)
    story.append(Paragraph(F"===== Report from {basename} =====", styles['Heading2']))
    story.append(Spacer(1,6))

    cols_to_keep = column_map.get(file_path, None)
    try:
      df = read_and_scrub_csv(file_path, cols_to_keep)
    except Exception as e:
      story.append(Paragraph(f"<i>Error reading {basename}: {e}</i>", styles['BodyText']))
      story.append(Spacer(1, 12))
      continue
    story.append(Paragraph(f"Source file: {basename} - rows: {len(df)} - columns: {len(df.columns)}", styles['Normal']))
    story.append(Spacer(1,6))

    if len(df) == 0 or len(df.columns) == 0:
      story.append(Paragraph("<i>No data available after scrubbing.</i>", styles['BodyText']))
      story.append(Spacer(1,12))
    else: 
      table = df_to_reportlab_table(df, styles, available_width)
      story.append(table)
      story.append(Spacer(1, 18))

    if ix < len(csv_files):
      story.append(PageBreak())

  doc.build(story)
  print(f"[INFO] PDF created: {output_file}")
  return output_file

# Sends email with attachment
def send_email_with_attachment(sender_email: str, app_password: str, recipients: List[str], subject: str, body: str, attachment_path: str, smtp_server: str = "smtp.gmail.vom", smtp_port: int = 587):
  msg = MIMEMultipart()
  msg["From"] = sender_email
  msg["To"] = ", ".join(recipients)
  msg["Subject"] = subject
  msg.attach(MIMEText(body, "plain"))

  with open(attachement_path, "rb") as f:
    part  MIMEBase("application", "octet-stream")
    part.set_payload(f.read())
  encoders.encode_base64(part)
  part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(attachment_path)}"')
  msg.attach(part)

  context = ssl.create_default_context()
  server = smtplib.SMTP(smtp_server, smtp_port, timeeout=30)
  server.ehlo()
  if smtp_server != "localhost" and smtop_port == 587:
    server.starttls(context=context)
    server.ehlo(
  server.login(sender_email, app_password)
  server.sendmail(sender_email, recipients, msg.as_string())
  server.qit()
  print("[INFO] Email sent (attempted).")

#CLI - Example Run
if __name__ == "__main__":
    csv_folder = "csvs"
    csv_files = sorted(glob.glob(os.path.join(csv_folder, "*.csv")))[:4]
    if len (csv_files) == 0:
      print("[WARN] No CSVs found in 'csvs/' - create sample CSV files to test.")
    column_map = {fp: None for fp in csv_files} #This keeps all columns
    output_pdf = "weekly_report.pdf"
    create_pdf_report(csv_files, column_map, output_file=output_pdf)

    #Email if env vars set
    sender = os.environ.get("GMAIL_USER")
    app_pw = os.environ.get("GMAIL_APP_PASSWORD")
    recipient_list = [os.environ.get("REPORT_RECIPIENT", sender)] if sender else []

    if sender nd app_pw and recipient_list:
      try:
        send_email_with_attachment(sender, app_pw, recipient_list, "Weekly Combined Report", "Attached is the weekly combined report.", output_pdf, smtp_server=os.environ.get("SMTP_HOST", "smtp.gmail.com"), smtp_port=int(os.environ.get("SMTP_PORT", "587")))
      except Exception as e:
        print(f"[ERROR] Email failed: {e}")
      else: print("[INFO] Email skipped - set GMAIL_USER & GMAIL_APP_PASSWORD env vars to enable.")
        
  

  
    
  
