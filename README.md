# Lab: Missing Input Validation — Vulnerable Registration App

**Educational use only.** `vulnerable_app.py` is *intentionally* insecure. It binds to
`127.0.0.1` only. Never deploy it or expose it to a network.

## What it demonstrates
A registration form (name, email, age, deposit) that performs **no validation**:
no length limits, no type/range checks, no output encoding.

| # | Abuse case | Input | Consequence |
|---|-----------|-------|-------------|
| 1 | Stored XSS | `name=<script>…</script>` | Attacker JS runs in every viewer's browser (CWE-79) |
| 2 | Negative / non-numeric values | `age=-5`, `deposit=-1000000`, `deposit=NaN` | Corrupt business data and totals (CWE-20, CWE-1284) |
| 3 | Overlong string | `name` = 5,000,000 chars ×3 | Unbounded storage + page bloat / DoS (CWE-770, CWE-400) |

## Run it
```bash
python3 vulnerable_app.py          # terminal 1  -> http://127.0.0.1:8000
pip install playwright && playwright install chromium
python3 exploit_demo.py            # terminal 2  -> writes evidence/
```

## Files
- `vulnerable_app.py` – the unvalidated application (stdlib only)
- `exploit_demo.py` – scripted abuse cases + screenshots
- `evidence/` – screenshots and `evidence.json` (raw requests/responses)
- `report/Lab_Report_Input_Validation.pdf` – full lab report
