import os
import sqlite3
from datetime import datetime

from typing import Optional
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from render import build_html, render_pdf
from report_data import get_report_data

app = FastAPI()

DB_PATH = "report.db"
REPORTS_DIR = "reports"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_reports_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()


@app.on_event("startup")
def on_startup():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    conn = get_connection()
    create_reports_table(conn)
    conn.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reports", status_code=201)
def create_report():
    conn = get_connection()

    report = get_report_data()
    html = build_html(report)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.execute(
        "INSERT INTO reports (path, created_at) VALUES (?, ?)", ("", now)
    )
    report_id = cursor.lastrowid
    file_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")

    render_pdf(html, file_path)

    conn.execute("UPDATE reports SET path = ? WHERE id = ?", (file_path, report_id))
    conn.commit()
    conn.close()

    return {"id": report_id, "file": f"/reports/{report_id}/file"}


@app.get("/reports/{report_id}")
def get_report(report_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, path, created_at FROM reports WHERE id = ?", (report_id,)
    ).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"id": row["id"], "created_at": row["created_at"], "file": f"/reports/{row['id']}/file"}


@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    conn = get_connection()
    row = conn.execute("SELECT path FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()

    if row is None or not os.path.exists(row["path"]):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(row["path"], media_type="application/pdf", filename=f"report-{report_id}.pdf")