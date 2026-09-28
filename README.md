# PDF Report Generator

FlyRank Internship · Backend Track · Week 4 · Assignment A8

A small pipeline that turns a SQLite database into a downloadable PDF sales
report: **query → render → store → serve.** No background jobs — the whole
thing runs inside one API endpoint.

## Dataset

**Option A — the little shop.** `seed.py` fills `report.db` with 200 random
orders (6 products, random amounts between $5–$200, random dates over the
last 30 days). The seed script deletes all rows before inserting, so it's
safe to run more than once — the row count always ends up at 200.

## Stack

- Python 3.12
- FastAPI + Uvicorn
- SQLite (built-in `sqlite3` module)
- Playwright (headless Chromium) for HTML → PDF rendering

## How to run

```bash
# 1. Install dependencies
pip install fastapi uvicorn playwright
playwright install chromium

# 2. Seed the database
python seed.py

# 3. Start the API
uvicorn main:app --port 8000
```

The API is now live at `http://localhost:8000`.

## Endpoints

| Method | Path                  | What it does                                       |
|--------|-----------------------|------------------------------------------------------|
| GET    | `/health`             | `{ "status": "ok" }`                                |
| POST   | `/reports`            | Runs the pipeline, returns `201` + `{ id, file }`    |
| GET    | `/reports/:id`        | Returns the report row, or `404` if unknown          |
| GET    | `/reports/:id/file`   | Streams the PDF from disk                            |

`POST /reports` accepts an optional JSON body `{ "force": true }` to skip
the once-per-day check and always generate a fresh report.

## The aggregation SQL (Stage 2)

```sql
-- Total orders
SELECT COUNT(*) AS n FROM orders;

-- Total revenue
SELECT SUM(amount) AS total FROM orders;

-- Top 5 products by revenue
SELECT product, SUM(amount) AS revenue
FROM orders
GROUP BY product
ORDER BY revenue DESC
LIMIT 5;

-- Orders per day, last 7 days
SELECT DATE(created_at) AS day, COUNT(*) AS count
FROM orders
WHERE DATE(created_at) >= DATE('now', '-6 days')
GROUP BY day
ORDER BY day;
```

## POST → download proof

[PASTE HERE — your PowerShell output from the Stage 4 checkpoint, e.g.
the `$r1 = Invoke-RestMethod -Method Post ...` block and the
`Invoke-WebRequest ... -OutFile my-report.pdf` / opening it]

## Duplicate requests → one file (Stage 5)

[PASTE HERE — your `$r1` / `$r2` output showing the same id twice, plus
the `force: true` output showing a different id]

## Stage 4 & 5 notes

**Stage 4 — when would this move out of the request?** Right now `POST
/reports` takes about 4 seconds because it launches Chromium and renders
the PDF inline. That's fine for one user clicking one button, but it would
become a problem with a bigger dataset or many concurrent users hitting the
endpoint at once — at that point I'd move generation into a background job
(the A7 pattern: return `202 Accepted` immediately, do the work
asynchronously, and let the client poll `GET /reports/:id` for a `pending`
→ `done` status).

**Stage 5 — what does the once-per-day check protect against, and what
does a missing check cost in the real world?** It protects against a
double-clicked "Generate report" button creating duplicate files and rows
for no reason. A real-world example: an e-commerce system that emails an
order confirmation — without an idempotency check, a flaky network causing
the client to retry a request could result in the customer getting charged,
or emailed, twice.

## Screenshot — page 1 of a generated report

[PASTE HERE — drop your page-1 screenshot image into the repo folder,
e.g. `screenshot-1.png`, then reference it like this:]

![Report page 1](screenshot-1.png)

## Project structure
