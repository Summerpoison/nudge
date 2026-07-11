from datetime import datetime

from flask import Flask, jsonify, request

from db import init_db
from models import create_task, get_all_tasks, get_task

app = Flask(__name__)
init_db()


@app.route("/health")
def health():
    return jsonify(status="ok", service="core-app")


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    name = data["name"]
    external_deadline = datetime.fromisoformat(data["external_deadline"])

    buffer_deadline = datetime.fromisoformat(data["buffer_deadline"]) if data.get("buffer_deadline") else None
    checkpoint_1 = datetime.fromisoformat(data["checkpoint_1"]) if data.get("checkpoint_1") else None
    checkpoint_2 = datetime.fromisoformat(data["checkpoint_2"]) if data.get("checkpoint_2") else None

    task = create_task(name, external_deadline, buffer_deadline, checkpoint_1, checkpoint_2)
    return jsonify(task), 201


@app.route("/tasks", methods=["GET"])
def list_tasks():
    return jsonify(get_all_tasks())


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task_route(task_id):
    task = get_task(task_id)
    if task is None:
        return jsonify(error="not found"), 404
    return jsonify(task)


if __name__ == "__main__":
    app.run(port=3000, debug=True)
