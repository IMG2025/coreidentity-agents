from flask import Flask, jsonify, request
import threading
import os
import time
import psycopg2
import uuid
import json
from datetime import datetime

from maven import start_maven

app = Flask(__name__)

# === Pulse Agent ===
class Pulse:
    def __init__(self):
        self.metrics = []
        self.last_ping = time.ctime()

    def ping(self, source="system"):
        self.last_ping = time.ctime()
        entry = f"[{self.last_ping}] Pulse ping from {source}"
        print(entry)
        self.metrics.append(entry)
        return {"status": "ok", "source": source, "time": self.last_ping}

    def status(self):
        return {"agent": "Pulse", "last_ping": self.last_ping, "total_events": len(self.metrics)}

    def logs(self):
        return self.metrics

pulse = Pulse()

# === Deployr Agent ===
class Deployr:
    def __init__(self):
        self.deployed_services = []

    def deploy(self, service):
        timestamp = time.ctime()
        entry = f"[{timestamp}] Deployed {service}"
        print(entry)
        self.deployed_services.append(entry)
        return {"status": "deployed", "service": service, "time": timestamp}

deployr = Deployr()

# === Supplier Agent ===
class Supplier:
    def __init__(self):
        self.suppliers = []

    def sync(self, supplier_name):
        timestamp = time.ctime()
        entry = f"[{timestamp}] Supplier {supplier_name} synced."
        print(entry)
        self.suppliers.append(entry)
        return {"status": "synced", "supplier": supplier_name, "time": timestamp}

supplier = Supplier()

# === VIA Agent ===
class VIA:
    def __init__(self):
        self.sessions = []

    def track_session(self, user_id, session_data):
        timestamp = time.ctime()
        entry = f"[{timestamp}] Session started for user {user_id}"
        print(entry)
        self.sessions.append(entry)
        return {"status": "tracked", "user": user_id, "time": timestamp}

via = VIA()

# === Echo Agent ===
class Echo:
    def __init__(self):
        self.logs = []

    def log_action(self, user_action):
        timestamp = time.ctime()
        entry = f"[{timestamp}] User action: {user_action}"
        print(entry)
        self.logs.append(entry)
        return {"status": "logged", "action": user_action, "time": timestamp}

echo = Echo()

# === Signal Agent ===
class Signal:
    def __init__(self):
        self.security_events = []

    def detect_violation(self, violation_detail):
        timestamp = time.ctime()
        entry = f"[{timestamp}] Violation detected: {violation_detail}"
        print(entry)
        self.security_events.append(entry)
        return {"status": "violation_detected", "detail": violation_detail, "time": timestamp}

signal = Signal()

# === MCP Agent ===
class MCP:
    def __init__(self):
        self.activity_log = []

    def intercept(self, source, target, message):
        timestamp = time.ctime()
        entry = {
            "timestamp": timestamp,
            "source": source,
            "target": target,
            "message": message
        }
        self.activity_log.append(entry)
        print(f"[MCP] Intercept from {source} to {target}: {message}")
        return entry

mcp = MCP()

@app.route("/")
def home():
    return "CoreIdentity Platform Online"

@app.route("/ping")
def ping():
    try:
        with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO edge_logs (id, created_at, source, action, metadata, extra)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    datetime.utcnow(),
                    "Pulse",
                    "ping",
                    json.dumps({"source": "system"}),
                    "Automated ping"
                ))
                conn.commit()
    except Exception as e:
        print("[ERROR] /ping failed to log:", e)
    return jsonify(pulse.ping())

@app.route("/pulse")
def pulse_status():
    return jsonify(pulse.status())

@app.route("/logs/pulse")
def pulse_logs():
    return jsonify(pulse.logs())

@app.route("/deployr/<service>")
def deploy_service(service):
    return jsonify(deployr.deploy(service))

@app.route("/supplier/<supplier_name>")
def sync_supplier(supplier_name):
    return jsonify(supplier.sync(supplier_name))

@app.route("/via/<user_id>")
def track_via(user_id):
    session_data = {"example": "session_data"}
    return jsonify(via.track_session(user_id, session_data))

@app.route("/echo/<user_action>")
def echo_log(user_action):
    return jsonify(echo.log_action(user_action))

@app.route("/signal/<violation_detail>")
def detect_violation(violation_detail):
    return jsonify(signal.detect_violation(violation_detail))

@app.route("/mcp/intercept", methods=["POST"])
def mcp_intercept():
    data = request.json
    source = data.get("source", "unknown")
    target = data.get("target", "unknown")
    message = data.get("message", {})
    result = mcp.intercept(source, target, message)
    with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO edge_logs (id, created_at, source, action, metadata, extra)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                datetime.utcnow(),
                source,
                "mcp_intercept",
                json.dumps({"target": target, "message": message}),
                "MCP route invoked"
            ))
            conn.commit()
    return jsonify({"status": "intercepted", "details": result}), 200

@app.route("/log/signal", methods=["POST"])
def log_signal():
    try:
        data = request.json
        with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO signal_events (id, timestamp, source, payload, routed_to, result)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    data.get("timestamp", datetime.utcnow().isoformat()),
                    data.get("source", "sentinel"),
                    json.dumps(data.get("payload", {})),
                    data.get("routed_to", "n/a"),
                    data.get("result", "blocked")
                ))
                conn.commit()
        return jsonify({"status": "signal logged"}), 200
    except Exception as e:
        print("[ERROR] /log/signal failed:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/log/sentinel/intercept", methods=["POST"])
def log_intercept():
    try:
        data = request.json
        with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO edge_logs (id, created_at, source, action, metadata, extra)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    datetime.utcnow(),
                    data.get("source", "Sentinel"),
                    data.get("action", "intercept"),
                    json.dumps(data.get("metadata", {})),
                    data.get("extra", "N/A")
                ))
                conn.commit()
        return jsonify({"status": "intercept logged"}), 200
    except Exception as e:
        print("[ERROR] /log/sentinel/intercept failed:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/logs")
def view_logs():
    try:
        with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, created_at, source, action, metadata FROM edge_logs ORDER BY created_at DESC LIMIT 25;")
                rows = cur.fetchall()
                logs = [
                    {
                        "id": row[0],
                        "timestamp": row[1].strftime("%Y-%m-%d %H:%M:%S") if row[1] else "N/A",
                        "source": row[2],
                        "action": row[3],
                        "metadata": row[4]
                    }
                    for row in rows
                ]
        return jsonify(logs), 200
    except Exception as e:
        print("[/logs] Dashboard error:", e)
        return jsonify({"error": str(e)}), 500

threading.Thread(target=start_maven, daemon=True).start()
print("[MAIN] Launched start_maven() successfully")
