#!/usr/bin/env python3
"""
INTENTIONALLY VULNERABLE registration app -- FOR EDUCATIONAL LAB USE ONLY.

It accepts a registration form (name, email, age, deposit) and performs
NO input validation of any kind:
  * no length limits
  * no type / range checks
  * no output encoding (HTML escaping)

Do NOT deploy this anywhere. Binds to 127.0.0.1 only.
Run:  python3 vulnerable_app.py   ->  http://127.0.0.1:8000
"""
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

DB = "users.db"


def db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, age TEXT, deposit TEXT)""")
    return con


FORM = """<html><head><title>Register</title></head><body>
<h1>Registration</h1>
<form method="POST" action="/register">
  Name: <input name="name"><br>
  Email: <input name="email"><br>
  Age: <input name="age"><br>
  Initial deposit (INR): <input name="deposit"><br>
  <input type="submit" value="Register">
</form>
<p><a href="/users">View all users</a></p>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, code=200):
        data = body.encode("utf-8", "replace")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(FORM)
        elif self.path == "/users":
            con = db()
            rows = con.execute("SELECT id,name,email,age,deposit FROM users").fetchall()
            total = 0.0
            out = "<html><body><h1>Registered users</h1><table border=1>"
            out += "<tr><th>ID</th><th>Name</th><th>Email</th><th>Age</th><th>Deposit</th></tr>"
            for r in rows:
                # VULNERABILITY: values written straight into HTML (no escaping)
                out += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
                try:
                    total += float(r[4])      # VULNERABILITY: trusts stored value
                except ValueError:
                    pass
            out += f"</table><p>Total bank deposits: {total}</p>"
            out += '<p><a href="/">Back</a></p></body></html>'
            self._send(out)
        else:
            self._send("Not found", 404)

    def do_POST(self):
        if self.path != "/register":
            return self._send("Not found", 404)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", "replace")   # no size cap
        f = parse_qs(body, keep_blank_values=True)
        name = f.get("name", [""])[0]
        email = f.get("email", [""])[0]
        age = f.get("age", [""])[0]
        deposit = f.get("deposit", [""])[0]
        # VULNERABILITY: stored exactly as received -- no validation
        con = db()
        con.execute("INSERT INTO users(name,email,age,deposit) VALUES (?,?,?,?)",
                    (name, email, age, deposit))
        con.commit()
        self._send(f"<html><body>Welcome, {name}! (stored {len(name)} chars)"
                   f'<br><a href="/users">View users</a></body></html>')

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("Vulnerable app on http://127.0.0.1:8000  (educational use only)")
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
