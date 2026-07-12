from datetime import datetime

from flask import Flask, abort, jsonify, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from db import init_db
from models import (
    add_task_event,
    buffer_progress_percent,
    create_task,
    get_all_tasks,
    get_task,
    get_task_events,
    is_checkpoint_due,
    set_focus_tasks,
    update_task_status,
)
from uploads import delete_attachment, list_attachments, save_attachment, task_upload_dir

app = Flask(__name__)
init_db()


def friendly_date(value):
    if not value:
        return ""
    return datetime.fromisoformat(value).strftime("%b %d, %Y %I:%M %p")


app.jinja_env.filters["friendly_date"] = friendly_date


@app.route("/health")
def health():
    return jsonify(status="ok", service="core-app")


# --- HTML pages ---


@app.route("/")
def dashboard():
    active_tasks = [t for t in get_all_tasks() if t["status"] == "active"]
    next_task = active_tasks[0] if active_tasks else None
    other_tasks = active_tasks[1:]
    return render_template("dashboard.html", next_task=next_task, other_tasks=other_tasks)


@app.route("/tasks", methods=["GET", "POST"])
def all_tasks():
    if request.method == "POST":
        name = request.form["name"]
        external_deadline = datetime.fromisoformat(request.form["external_deadline"])
        create_task(name, external_deadline)
        return redirect(url_for("all_tasks"))
    return render_template("all_tasks.html", tasks=get_all_tasks())


@app.route("/tasks/<int:task_id>")
def task_detail(task_id):
    task = get_task(task_id)
    if task is None:
        abort(404)
    return render_template(
        "task_detail.html",
        task=task,
        events=get_task_events(task_id),
        attachments=list_attachments(task_id),
        buffer_pct=buffer_progress_percent(task),
        checkpoint_due=is_checkpoint_due(task),
    )


@app.route("/tasks/<int:task_id>/checkin")
def checkin(task_id):
    task = get_task(task_id)
    if task is None:
        abort(404)
    return render_template("checkin.html", task=task)


@app.route("/tasks/<int:task_id>/triage", methods=["GET", "POST"])
def triage(task_id):
    task = get_task(task_id)
    if task is None:
        abort(404)
    if request.method == "POST":
        reason = request.form["reason"]
        recipient = request.form["recipient"]
        update_task_status(task_id, "on_hold")
        add_task_event(task_id, "triage_draft_sent", f"Blocker triage ({reason}): draft sent to {recipient}")
        return redirect(url_for("task_detail", task_id=task_id))
    return render_template("triage.html", task=task)


@app.route("/tasks/<int:task_id>/triage/timer", methods=["POST"])
def start_timer(task_id):
    task = get_task(task_id)
    if task is None:
        abort(404)
    add_task_event(task_id, "sprint_started", "Started a 10-minute focus timer")
    return redirect(url_for("focus_timer", task_id=task_id))


@app.route("/tasks/<int:task_id>/timer")
def focus_timer(task_id):
    task = get_task(task_id)
    if task is None:
        abort(404)
    return render_template("timer.html", task=task)


@app.route("/tasks/<int:task_id>/upload", methods=["POST"])
def upload_attachment(task_id):
    task = get_task(task_id)
    if task is None:
        abort(404)
    file = request.files.get("artifact")
    if file and file.filename:
        filename = save_attachment(task_id, file)
        add_task_event(task_id, "artifact_submitted", f"Artifact submitted: {filename}")
    return redirect(url_for("task_detail", task_id=task_id))


@app.route("/tasks/<int:task_id>/uploads/<filename>")
def view_attachment(task_id, filename):
    return send_from_directory(task_upload_dir(task_id), secure_filename(filename))


@app.route("/tasks/<int:task_id>/uploads/<filename>/delete", methods=["POST"])
def delete_attachment_route(task_id, filename):
    task = get_task(task_id)
    if task is None:
        abort(404)
    if delete_attachment(task_id, filename):
        add_task_event(task_id, "attachment_removed", f"Attachment removed: {filename}")
    return redirect(url_for("task_detail", task_id=task_id))


@app.route("/tasks/<int:task_id>/status", methods=["POST"])
def change_status(task_id):
    task = get_task(task_id)
    if task is None:
        abort(404)
    new_status = request.form["status"]
    update_task_status(task_id, new_status)
    add_task_event(task_id, "status_changed", f"Status changed to {new_status.replace('_', ' ').title()}")
    return redirect(url_for("task_detail", task_id=task_id))


# --- JSON API (polled by the notification-worker, Part C) ---


@app.route("/api/tasks", methods=["POST"])
def api_create_task():
    data = request.get_json()
    name = data["name"]
    external_deadline = datetime.fromisoformat(data["external_deadline"])

    buffer_deadline = datetime.fromisoformat(data["buffer_deadline"]) if data.get("buffer_deadline") else None
    checkpoint_1 = datetime.fromisoformat(data["checkpoint_1"]) if data.get("checkpoint_1") else None
    checkpoint_2 = datetime.fromisoformat(data["checkpoint_2"]) if data.get("checkpoint_2") else None

    task = create_task(name, external_deadline, buffer_deadline, checkpoint_1, checkpoint_2)
    return jsonify(task), 201


@app.route("/api/tasks", methods=["GET"])
def api_list_tasks():
    return jsonify(get_all_tasks())


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def api_get_task(task_id):
    task = get_task(task_id)
    if task is None:
        return jsonify(error="not found"), 404
    return jsonify(task)


@app.route("/api/tasks/focus", methods=["POST"])
def api_set_focus_tasks():
    data = request.get_json()
    task_ids = data["task_ids"]
    applied = set_focus_tasks(task_ids)
    for task_id in applied:
        add_task_event(task_id, "marked_focus_task", "Marked as a focus task for this week")
    return jsonify(focus_task_ids=applied)


if __name__ == "__main__":
    app.run(port=3000, debug=True)
