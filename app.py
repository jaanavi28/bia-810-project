import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "atelier-secret-key-2024")

# Anthropic API key — set via environment variable ANTHROPIC_API_KEY
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Simple user store — replace with a database for production
USERS = {
    "admin": "password123",
    "demo": "demo123",
}

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/api/chat", methods=["POST"])
def chat_proxy():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    payload = request.get_json()
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        json=payload,
        timeout=60,
    )
    return jsonify(resp.json()), resp.status_code

@app.errorhandler(500)
def internal_error(e):
    import traceback
    return f"<pre>{traceback.format_exc()}</pre>", 500

if __name__ == "__main__":
    app.run(debug=True)
