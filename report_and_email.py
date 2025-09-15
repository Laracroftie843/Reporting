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
