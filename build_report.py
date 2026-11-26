#!/usr/bin/env python3
"""Generates report/Lab_Report_Input_Validation.pdf from the code + evidence."""
import json
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Image, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle,
                                KeepTogether)
from PIL import Image as PILImage

ev = json.load(open("evidence/evidence.json"))
OUT = "report/Lab_Report_Input_Validation.pdf"

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=15, spaceBefore=10, spaceAfter=6,
                    textColor=colors.HexColor("#1f3a5f"))
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=11.5, spaceBefore=8, spaceAfter=4,
                    textColor=colors.HexColor("#1f3a5f"))
BODY = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10, leading=14, spaceAfter=5)
CELL = ParagraphStyle("C", parent=BODY, fontSize=8.5, leading=11, spaceAfter=0)
MONO = ParagraphStyle("M", parent=CELL, fontName="Courier", fontSize=7.5, leading=9.5)
CAP = ParagraphStyle("Cap", parent=BODY, fontSize=8.5, textColor=colors.HexColor("#555555"),
                     alignment=1)
TITLE = ParagraphStyle("T", parent=ss["Title"], fontSize=21, leading=26,
                       textColor=colors.HexColor("#1f3a5f"))
CODE = ParagraphStyle("Code", fontName="Courier", fontSize=6.0, leading=6.9)


def code_block(path):
    lines = open(path).read().splitlines()
    w = len(str(len(lines)))
    txt = "\n".join(f"{i + 1:>{w}}  {l}" for i, l in enumerate(lines))
    return Preformatted(txt, CODE)


def img(path, max_w=165 * mm):
    w, h = PILImage.open(path).size
    s = min(max_w / w, 1.0 if w < 900 else max_w / w)
    return Image(path, width=w * s * (max_w / (w * s)) if False else max_w, height=h * (max_w / w))


def kv_table(rows, col=(38 * mm, 128 * mm)):
    data = [[Paragraph(f"<b>{escape(k)}</b>", CELL),
             v if not isinstance(v, str) else Paragraph(v, CELL)] for k, v in rows]
    t = Table(data, colWidths=col)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b8c2cc")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2f7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


def mono(s):
    return Paragraph(escape(s).replace("\n", "<br/>"), MONO)


def footer(c, d):
    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(18 * mm, 10 * mm, "Lab Report - Missing Input Validation (educational use only)")
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {d.page}")
    c.restoreState()


doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=16 * mm, bottomMargin=18 * mm,
                        title="Lab Report: Missing Input Validation",
                        author="Student")
S = []

# ------------------------------------------------------------------ cover
S += [Spacer(1, 30 * mm),
      Paragraph("Lab Report", TITLE),
      Paragraph("Exploiting an Application with No Input Validation", ParagraphStyle(
          "sub", parent=BODY, fontSize=13, alignment=1, textColor=colors.HexColor("#444444"))),
      Spacer(1, 14 * mm),
      kv_table([
          ("Course", "Secure Coding / Application Security"),
          ("Lab topic", "Input validation failures (XSS, invalid numeric input, oversized input)"),
          ("Student", "&lt;Your name&gt; &nbsp;&nbsp; Roll / ID: &lt;your ID&gt;"),
          ("Date", "26 November 2026"),
          ("Repository", "https://github.com/&lt;your-username&gt;/&lt;repo-name&gt;"),
          ("Environment", "Python 3.12, SQLite, Chromium (headless, via Playwright); "
                          "application bound to 127.0.0.1 only"),
      ]),
      Spacer(1, 10 * mm),
      Paragraph("<i>Ethics note: the application is intentionally vulnerable and was run only on "
                "the local loopback interface. All payloads were sent to my own instance. "
                "Do not run this code on, or aim these techniques at, systems you do not own or "
                "have written permission to test.</i>", BODY),
      PageBreak()]

# ------------------------------------------------------------------ 1 aim
S += [Paragraph("1. Aim", H1),
      Paragraph("To build a small web application that accepts user input with <b>no validation "
                "whatsoever</b>, to demonstrate concrete abuse cases against it, and to document "
                "for each case the input sent, the observed behaviour of the application and the "
                "security consequence. The lab then analyses the root cause and the controls that "
                "would have prevented each issue.", BODY),
      Paragraph("Objectives", H2),
      Paragraph("&bull; Implement a registration form (name, email, age, deposit) with no length, "
                "type, range or encoding controls.<br/>"
                "&bull; Demonstrate three abuse cases: stored cross-site scripting, negative / "
                "non-numeric values, and an overlong string.<br/>"
                "&bull; Capture reproducible evidence (HTTP responses, raw HTML, screenshots).<br/>"
                "&bull; Map each weakness to CWE / OWASP categories and describe remediation.", BODY)]

# ------------------------------------------------------------------ 2 design
S += [Paragraph("2. Application Design", H1),
      Paragraph("The target is a single-file Python web app using only the standard library "
                "(<font face='Courier'>http.server</font> + <font face='Courier'>sqlite3</font>). "
                "It exposes three routes:", BODY),
      kv_table([("GET /", "Renders the registration form."),
                ("POST /register", "Reads name, email, age, deposit from the request body and "
                                   "stores them exactly as received (no validation). Echoes the "
                                   "name back in an HTML response."),
                ("GET /users", "Lists all users, writing each value directly into the HTML, and "
                               "computes the sum of all deposits by trusting the stored values.")]),
      Spacer(1, 3 * mm),
      Paragraph("<b>Deliberate flaws</b> (each marked <font face='Courier'>VULNERABILITY</font> "
                "in the source): (a) no maximum length on any field or on the request body; "
                "(b) age and deposit are stored as free text with no type or range check; "
                "(c) user-controlled values are interpolated into HTML without escaping. "
                "SQL statements use bound parameters, so SQL injection is deliberately out of "
                "scope for this lab.", BODY),
      Paragraph("<b>Baseline (legitimate input).</b> Registering <font face='Courier'>Alice, "
                "alice@example.com, 30, 5000</font> returns "
                f"<font face='Courier'>{escape(ev['baseline']['response'][:70])}...</font> "
                "and the record displays normally:", BODY),
      Image("evidence/baseline.png", width=120 * mm, height=120 * mm * 220 / 900),
      Paragraph("Figure 1 - Baseline: a well-formed registration is stored and displayed.", CAP),
      PageBreak()]

# ------------------------------------------------------------------ 3 code
S += [Paragraph("3. Code Listing", H1),
      Paragraph("3.1 vulnerable_app.py (the unvalidated application)", H2),
      code_block("vulnerable_app.py"),
      PageBreak(),
      Paragraph("3.2 exploit_demo.py (abuse-case driver and evidence collector)", H2),
      code_block("exploit_demo.py"),
      PageBreak()]

# ------------------------------------------------------------------ 4 abuse
a1, a2a, a2b, a3 = ev["abuse1"], ev["abuse2a"], ev["abuse2b"], ev["abuse3"]

S += [Paragraph("4. Abuse Scenarios", H1),
      Paragraph("Each scenario was run against a freshly reset database so results do not "
                "interfere with each other. Raw evidence is in <font face='Courier'>"
                "evidence/evidence.json</font>.", BODY),
      Paragraph("Scenario 1 - Stored cross-site scripting (XSS) via the name field", H2),
      kv_table([
          ("Field / vector", "<font face='Courier'>name</font> in POST /register"),
          ("Input sent", mono(a1["payload"])),
          ("Application behaviour",
           f"HTTP 200. The payload was stored verbatim ({len(a1['payload'])} characters) and echoed back unescaped "
           "in the welcome page. On GET /users it appears in the page source as a live "
           "<font face='Courier'>&lt;script&gt;</font> element (see raw row below). Loading "
           "/users in a browser executed the script: the page title changed to "
           "<font face='Courier'>" + escape(a1["page_title_after_load"]) + "</font> and a red "
           "banner was injected. The victim's name cell renders blank because the browser treats "
           "the value as code, not text."),
          ("Raw HTML evidence", mono(a1["raw_html_row"])),
          ("Security consequence",
           "Persistent (stored) XSS: any visitor to /users runs attacker-controlled JavaScript "
           "in the application's origin. In a real app this enables session-cookie theft "
           "(<font face='Courier'>document.cookie</font> - empty here only because this demo "
           "sets no cookie), account takeover, forced actions, keylogging, phishing overlays and "
           "defacement. One malicious registration harms every later viewer, including "
           "administrators."),
      ]),
      Spacer(1, 3 * mm),
      Image("evidence/abuse1_xss_executed.png", width=140 * mm, height=140 * mm * 300 / 900),
      Paragraph("Figure 2 - Scenario 1: injected script executed in the browser (red banner "
                "and changed page title).", CAP),
      PageBreak()]

S += [Paragraph("Scenario 2 - Negative and non-numeric values where positive numbers are required",
                H2),
      kv_table([
          ("Field / vector", "<font face='Courier'>age</font> and <font face='Courier'>deposit"
                             "</font> in POST /register"),
          ("Input sent (2a)", mono("name=Eve  age=-5  deposit=-1000000")),
          ("Input sent (2b)", mono("name=Bob  age=abc  deposit=NaN")),
          ("Application behaviour",
           "Both requests returned HTTP 200 and were stored. (2a) Eve is stored with age -5 and "
           "a deposit of -1,000,000. With Alice's legitimate 5,000 the page reports "
           "<font face='Courier'>" + escape(a2a["total_line"]) + "</font>. (2b) Python's "
           "<font face='Courier'>float()</font> accepts the string \"NaN\", so after adding "
           "Bob the page reports <font face='Courier'>" + escape(a2b["total_line"]) + "</font>; "
           "every later total is permanently poisoned until the row is removed. "
           "\"abc\" is stored as an age with no complaint."),
          ("Security consequence",
           "Business-logic and integrity failure (improper validation of a specified quantity). "
           "A negative deposit can reduce or invert balances, enable fraudulent credits or "
           "refunds, bypass limits, and corrupt reports. NaN/garbage values break calculations "
           "and can crash or mislead downstream systems (denial of service of the reporting "
           "feature). Impossible ages (-5) defeat age-gating and compliance checks."),
      ]),
      Spacer(1, 3 * mm),
      Image("evidence/abuse2a_negative.png", width=130 * mm, height=130 * mm * 260 / 900),
      Paragraph("Figure 3 - Scenario 2a: negative age and deposit accepted; total becomes "
                "-995,000.", CAP),
      Image("evidence/abuse2b_nan.png", width=130 * mm, height=130 * mm * 300 / 900),
      Paragraph("Figure 4 - Scenario 2b: non-numeric values accepted; total becomes NaN.", CAP),
      PageBreak()]

S += [Paragraph("Scenario 3 - Overlong string (unbounded input size)", H2),
      kv_table([
          ("Field / vector", "<font face='Courier'>name</font> in POST /register"),
          ("Input sent", mono("name = 'A' * 5,000,000   (one 5 MB field, sent 3 times)")),
          ("Application behaviour",
           "All three requests returned HTTP 200 in about 0.04-0.06 s each. The server read the "
           "entire body into memory with no size cap and confirmed "
           "<font face='Courier'>(stored 5000000 chars)</font>. The SQLite file grew to "
           f"{a3['db_file_bytes']:,} bytes and GET /users now returns a "
           f"{a3['users_page_bytes']:,}-byte page. The table layout is destroyed: the name "
           "column stretches far beyond the viewport and the real data is pushed off-screen."),
          ("Security consequence",
           "Resource-exhaustion / denial of service (CWE-770, CWE-400): an attacker can fill "
           "disk and memory and slow every page view with a few cheap requests; the damage "
           "persists because the data is stored. Pages also become unusable for legitimate "
           "users (layout/UI denial). <b>Note:</b> Python is memory-safe, so this lab shows "
           "the <i>resource</i> impact only. In a C/C++ program that copies such a string into "
           "a fixed-size buffer (e.g. <font face='Courier'>strcpy(buf, input)</font>), the same "
           "unchecked input becomes a classic buffer overflow (CWE-120/121) that can crash the "
           "process or allow code execution."),
      ]),
      Spacer(1, 3 * mm),
      Image("evidence/abuse3_overlong.png", width=140 * mm, height=140 * mm * 260 / 900),
      Paragraph("Figure 5 - Scenario 3: oversized values stretch the table and hide the real "
                "records.", CAP),
      Spacer(1, 4 * mm),
      Paragraph("Summary of results", H2)]

res = [[Paragraph(f"<b>{h}</b>", CELL) for h in
        ("#", "Payload", "Observed result", "Weakness (CWE / OWASP 2021)")],
       [Paragraph("1", CELL), Paragraph("&lt;script&gt;...&lt;/script&gt; in name", CELL),
        Paragraph("Script stored and executed for every viewer", CELL),
        Paragraph("CWE-79 Stored XSS; A03 Injection", CELL)],
       [Paragraph("2a", CELL), Paragraph("age=-5, deposit=-1000000", CELL),
        Paragraph("Accepted; total = -995000.0", CELL),
        Paragraph("CWE-20 / CWE-1284; A04 Insecure Design", CELL)],
       [Paragraph("2b", CELL), Paragraph("age=abc, deposit=NaN", CELL),
        Paragraph("Accepted; total = nan", CELL),
        Paragraph("CWE-20 / CWE-1284; A04 Insecure Design", CELL)],
       [Paragraph("3", CELL), Paragraph("5,000,000-char name x3", CELL),
        Paragraph(f"Accepted; DB {a3['db_file_bytes'] / 1e6:.1f} MB, page "
                  f"{a3['users_page_bytes'] / 1e6:.1f} MB", CELL),
        Paragraph("CWE-770 / CWE-400 (CWE-120 in C); A04", CELL)]]
t = Table(res, colWidths=(10 * mm, 50 * mm, 55 * mm, 51 * mm), repeatRows=1)
t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b8c2cc")),
                       ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dfe7f1")),
                       ("VALIGN", (0, 0), (-1, -1), "TOP")]))
S += [t, PageBreak()]

# ------------------------------------------------------------------ 5 analysis
S += [Paragraph("5. Security Analysis", H1),
      Paragraph("Root cause", H2),
      Paragraph("All three issues share one root cause: the application <b>trusts data that "
                "crosses a trust boundary</b>. The browser (or any HTTP client - an attacker does "
                "not need the form at all) can send arbitrary bytes, and the server treated them "
                "as well-formed, safe and bounded. Client-side HTML limits would not help, as they "
                "are trivially bypassed with curl or a proxy.", BODY),
      Paragraph("Impact by CIA triad", H2),
      Paragraph("&bull; <b>Confidentiality</b> - XSS can exfiltrate session tokens and page "
                "data.<br/>"
                "&bull; <b>Integrity</b> - XSS can act as the victim; negative / NaN values corrupt "
                "financial data.<br/>"
                "&bull; <b>Availability</b> - oversized input exhausts disk, memory and bandwidth, "
                "and NaN breaks reporting.", BODY),
      Paragraph("Remediation (not implemented in the lab code, by design)", H2),
      kv_table([
          ("Scenario 1 - XSS",
           "Context-aware <b>output encoding</b> on every render (e.g. "
           "<font face='Courier'>html.escape()</font> or an auto-escaping template engine); "
           "allow-list validation of names; a Content-Security-Policy header that forbids inline "
           "scripts; <font face='Courier'>HttpOnly</font> + <font face='Courier'>SameSite"
           "</font> cookies."),
          ("Scenario 2 - numbers",
           "Parse to a strict type and enforce a range server-side: reject non-finite values "
           "(<font face='Courier'>math.isfinite</font>), require 0 &lt;= age &lt;= 120 and "
           "deposit &gt; 0 with an upper bound; use <font face='Courier'>Decimal</font> or "
           "integer minor units for money; add a database <font face='Courier'>CHECK</font> "
           "constraint as defence in depth."),
          ("Scenario 3 - length",
           "Cap the request body (e.g. 16 KB) before reading it, enforce per-field maximum "
           "lengths (e.g. name &lt;= 100), add rate limiting, and in C/C++ use bounded APIs "
           "(<font face='Courier'>snprintf</font>, <font face='Courier'>strncpy</font> with "
           "explicit termination, or safe string types)."),
      ]),
      Spacer(1, 1 * mm),
      Paragraph("A minimal validator illustrating the principle (<b>allow-list, fail closed, "
                "server-side</b>):", BODY),
      Preformatted(
          "import math, re\n"
          "def validate(name, email, age, deposit):\n"
          "    if not (1 <= len(name) <= 100 and re.fullmatch(r\"[\\w .'-]+\", name)):\n"
          "        raise ValueError('bad name')\n"
          "    if len(email) > 254 or not re.fullmatch(r'[^@\\s]+@[^@\\s]+\\.[^@\\s]+', email):\n"
          "        raise ValueError('bad email')\n"
          "    age = int(age)                      # raises on 'abc'\n"
          "    if not 0 <= age <= 120: raise ValueError('bad age')\n"
          "    deposit = float(deposit)\n"
          "    if not math.isfinite(deposit) or not 0 < deposit <= 1_000_000:\n"
          "        raise ValueError('bad deposit')\n"
          "    return name, email, age, deposit\n", CODE),
      Spacer(1, 3 * mm),
      Paragraph("Principle: validate on <b>input</b> (type, length, range, format) <i>and</i> "
                "encode on <b>output</b>. Neither replaces the other.", BODY)]

# ------------------------------------------------------------------ 6 result
S += [Paragraph("6. Result and Conclusion", H1),
      Paragraph("The unvalidated application accepted every malicious input without complaint. "
                "All three abuse cases were reproduced and evidenced:", BODY),
      Paragraph("&bull; A <b>script tag</b> submitted as a name was stored and executed in the "
                "browser of anyone viewing the user list (stored XSS).<br/>"
                "&bull; <b>Negative</b> and <b>non-numeric</b> age/deposit values were accepted, "
                "producing a negative total (-995,000) and a NaN total.<br/>"
                "&bull; A <b>5 MB string</b>, sent three times, grew the database to ~15 MB, "
                "produced a ~15 MB page and broke the layout (resource exhaustion).", BODY),
      Paragraph("These results confirm that missing input validation is not a single bug but a "
                "class of vulnerabilities spanning injection, data-integrity and availability "
                "failures. Server-side allow-list validation, strict typing and range checks, "
                "size limits and output encoding - applied together - close all three issues "
                "demonstrated here.", BODY)]

KEEP = [Paragraph("7. Repository Contents", H1),
      kv_table([("vulnerable_app.py", "Unvalidated application source"),
                ("exploit_demo.py", "Scripted abuse cases and screenshots"),
                ("evidence/", "baseline + 4 abuse screenshots, evidence.json"),
                ("report/", "This PDF report"),
                ("README.md", "Overview and run instructions")]),
      Spacer(1, 4 * mm),
      Paragraph("References: OWASP Top 10 (2021) A03 Injection, A04 Insecure Design; OWASP Input "
                "Validation Cheat Sheet; OWASP XSS Prevention Cheat Sheet; MITRE CWE-20, CWE-79, "
                "CWE-120, CWE-400, CWE-770, CWE-1284.", BODY)]
S += [KeepTogether(KEEP)]

doc.build(S, onFirstPage=footer, onLaterPages=footer)
print("built", OUT)
