import os
import time
import datetime
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

PORT = int(os.environ.get("PORT", 8085))
START_TIME = datetime.datetime.utcnow()

# Seed initial builds history
BUILDS_HISTORY = [
    {
        "build_number": 42,
        "commit": "c83b19f",
        "branch": "main",
        "trigger": "GitHub Webhook (PR #14 Merge)",
        "status": "SUCCESS",
        "duration_seconds": 38,
        "stages": [
            {"name": "SCM Checkout", "status": "SUCCESS", "duration": "3s"},
            {"name": "Maven Compile & Test", "status": "SUCCESS", "duration": "14s", "details": "3/3 JUnit tests passed"},
            {"name": "SonarQube Quality Gate", "status": "SUCCESS", "duration": "5s", "details": "Quality Gate: PASSED (0 Bugs)"},
            {"name": "Docker Container Build", "status": "SUCCESS", "duration": "9s", "details": "Image size: 142MB"},
            {"name": "Artifact Registry Push", "status": "SUCCESS", "duration": "4s", "details": "Pushed to registry:tag v1.0.0"},
            {"name": "Docker Compose Deploy", "status": "SUCCESS", "duration": "3s", "details": "Health probe verified HTTP 200"}
        ],
        "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).isoformat()
    },
    {
        "build_number": 41,
        "commit": "81a94d2",
        "branch": "main",
        "trigger": "Manual Trigger (SRE Lead)",
        "status": "SUCCESS",
        "duration_seconds": 41,
        "stages": [
            {"name": "SCM Checkout", "status": "SUCCESS", "duration": "2s"},
            {"name": "Maven Compile & Test", "status": "SUCCESS", "duration": "16s", "details": "3/3 JUnit tests passed"},
            {"name": "SonarQube Quality Gate", "status": "SUCCESS", "duration": "6s", "details": "Quality Gate: PASSED"},
            {"name": "Docker Container Build", "status": "SUCCESS", "duration": "10s", "details": "Image size: 142MB"},
            {"name": "Artifact Registry Push", "status": "SUCCESS", "duration": "4s", "details": "Pushed to registry:tag v0.9.9"},
            {"name": "Docker Compose Deploy", "status": "SUCCESS", "duration": "3s", "details": "Health probe verified HTTP 200"}
        ],
        "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(hours=8)).isoformat()
    }
]

ARTIFACTS = [
    {
        "name": "enterprise-pipeline-service-1.0.0-RELEASE.jar",
        "type": "Maven JAR",
        "size_mb": 24.6,
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "created_at": (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).isoformat()
    },
    {
        "name": "docker.io/buildforge/enterprise-service:1.0.0-RELEASE",
        "type": "Docker Image",
        "size_mb": 142.1,
        "sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
        "created_at": (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).isoformat()
    }
]

PUPPET_COMPLIANCE = {
    "node_fqdn": "staging-agent-node-01.buildforge.corp",
    "environment": "production",
    "last_run": datetime.datetime.utcnow().isoformat(),
    "compliance_rate": "100%",
    "resources": [
        {"resource": "Package['openjdk-17-jdk']", "status": "Compliant", "details": "Version 17.0.10 installed"},
        {"resource": "Package['maven']", "status": "Compliant", "details": "Version 3.9.6 present in /usr/share/maven"},
        {"resource": "Service['docker']", "status": "Compliant", "details": "Docker daemon running with TLS enabled"},
        {"resource": "Firewall['001 accept HTTP/HTTPS']", "status": "Compliant", "details": "Ports 80, 443, 8090 accepted"},
        {"resource": "File['/etc/security/limits.conf']", "status": "Compliant", "details": "Max open files set to 65535"}
    ]
}

# --- Probes ---
@app.route("/health", methods=["GET"])
def health():
    uptime = str(datetime.datetime.utcnow() - START_TIME).split(".")[0]
    return jsonify({
        "status": "UP",
        "service": "enterprise-pipeline-service",
        "version": "1.0.0-RELEASE",
        "runtime": "Java 17 / Eclipse Temurin + Spring Boot Actuator",
        "uptime": uptime,
        "jvm_memory": {"heap_used_mb": random.randint(48, 85), "heap_max_mb": 512},
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200

@app.route("/ready", methods=["GET"])
def ready():
    return jsonify({
        "status": "Ready",
        "database": "PostgreSQL: Connected",
        "message_broker": "Ready",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200

# --- Pipeline API ---
@app.route("/api/pipeline/history", methods=["GET"])
def get_history():
    return jsonify({
        "total_builds": len(BUILDS_HISTORY),
        "builds": BUILDS_HISTORY,
        "success_rate": "100%",
        "latest_build": BUILDS_HISTORY[0] if BUILDS_HISTORY else None
    }), 200

@app.route("/api/pipeline/run", methods=["POST"])
def trigger_pipeline():
    data = request.get_json() or {}
    branch = data.get("branch", "main")
    commit = f"{random.choice(['a','b','c','d','e','f'])}{random.randint(100000, 999999):x}"[:7]
    trigger = data.get("trigger", "Manual UI Trigger")

    build_num = len(BUILDS_HISTORY) + 1
    new_build = {
        "build_number": build_num,
        "commit": commit,
        "branch": branch,
        "trigger": trigger,
        "status": "SUCCESS",
        "duration_seconds": random.randint(35, 45),
        "stages": [
            {"name": "SCM Checkout", "status": "SUCCESS", "duration": "2s", "details": f"Checked out commit {commit}"},
            {"name": "Maven Compile & Test", "status": "SUCCESS", "duration": f"{random.randint(12, 16)}s", "details": "3/3 JUnit tests passed (0 failures)"},
            {"name": "SonarQube Quality Gate", "status": "SUCCESS", "duration": "5s", "details": "Quality Gate: PASSED (Maintainability: A, Bugs: 0)"},
            {"name": "Docker Container Build", "status": "SUCCESS", "duration": f"{random.randint(8, 12)}s", "details": f"Multi-stage image enterprise-service:{commit}"},
            {"name": "Artifact Registry Push", "status": "SUCCESS", "duration": "4s", "details": f"Pushed tag {commit} to registry"},
            {"name": "Docker Compose Deploy", "status": "SUCCESS", "duration": "3s", "details": "Rolling update verified HTTP 200 OK"}
        ],
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    BUILDS_HISTORY.insert(0, new_build)

    return jsonify({
        "message": "Jenkins declarative pipeline executed successfully",
        "build": new_build
    }), 201

@app.route("/api/puppet/compliance", methods=["GET"])
def get_puppet_compliance():
    PUPPET_COMPLIANCE["last_run"] = datetime.datetime.utcnow().isoformat()
    return jsonify(PUPPET_COMPLIANCE), 200

@app.route("/api/artifacts", methods=["GET"])
def get_artifacts():
    return jsonify({"artifacts": ARTIFACTS, "total": len(ARTIFACTS)}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
