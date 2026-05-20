#!/usr/bin/env python3
import os
import logging
from flask import Flask, request
import subprocess

# --- Paths ---
DOCS_DIR = "/home/ccai01admin/mkdocs/CLA_AI_KERET_2025_MKDOCS"
DOCKER_COMPOSE_DIR = DOCS_DIR
BRANCH = "develop"
PORT = int(os.environ.get("MKDOCS_WEBHOOK_PORT", 9102))

# --- Logging ---
LOG_DIR = "/home/ccai01admin/mkdocs/logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "mkdocs_webhook.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.getLogger('werkzeug').setLevel(logging.CRITICAL)

app = Flask(__name__)

@app.route("/payload", methods=["POST"])
def payload():
    data = request.get_json(silent=True) or {}
    branch_ref = data.get("ref", "")
    logging.info(f"Webhook received for branch: {branch_ref}")

    if branch_ref == f"refs/heads/{BRANCH}":

        git_cmd = ["/usr/bin/git", "-C", DOCS_DIR, "pull", "origin", BRANCH]

        try:
            result = subprocess.run(git_cmd, capture_output=True, text=True, check=True)
            logging.info(result.stdout)
        except subprocess.CalledProcessError as e:
            logging.error(e.stderr)
            return "Git pull failed", 500

        docker_cmd = [
            "docker", "compose",
            "-f", os.path.join(DOCKER_COMPOSE_DIR, "docker-compose.yml"),
            "up", "-d", "--build", "--force-recreate"
        ]

        try:
            result = subprocess.run(docker_cmd, capture_output=True, text=True, check=True)
            logging.info(result.stdout)
        except subprocess.CalledProcessError as e:
            logging.error(e.stderr)
            return "Docker update failed", 500

        return "Docs updated", 200

    return "Ignored", 200


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=PORT)