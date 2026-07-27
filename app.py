from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import threading
import uuid

from Gemni_Services import generate_caption
from Ai_Scheduler_Caption_Generator import build_weekly_calendar, save_calendar

app = Flask(__name__)
CORS(app)

CALENDAR_PATH = "output/foodpanda_content_calendar.csv"


FRONTEND_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")


jobs = {}
jobs_lock = threading.Lock()



@app.errorhandler(404)
def not_found(_e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(_e):
    return jsonify({"error": "Internal server error"}), 500




@app.route("/api/status")
def health_check():
    return jsonify({"message": "Foodpanda AI Backend Running"})




@app.route("/generate-caption", methods=["POST"])
def generate_caption_route():
    data = request.get_json(force=True) or {}

    required_fields = ["platform", "topic", "goal", "audience", "emoji", "language"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    result = generate_caption(
        platform=data["platform"],
        topic=data["topic"],
        goal=data["goal"],
        audience=data["audience"],
        emoji=data["emoji"],
        language=data["language"],
        market=data.get("market", "Pakistan"),
    )

    return jsonify({"result": result})




def _run_calendar_job(job_id, params):
    try:
        rows = build_weekly_calendar(**params)
        save_calendar(rows, path=CALENDAR_PATH)
        with jobs_lock:
            jobs[job_id] = {"status": "done", "calendar": rows}
    except Exception as e:
        with jobs_lock:
            jobs[job_id] = {"status": "error", "error": str(e)}


@app.route("/weekly-calendar/start", methods=["POST"])
def start_weekly_calendar():
    data = request.get_json(force=True) or {}

    params = dict(
        market=data.get("market", "Pakistan"),
        platform=data.get("platform", "Instagram"),
        start_date=data.get("start_date"),
        goal=data.get("goal", "Increase Engagement"),
        audience=data.get("audience", "Students"),
        emoji=data.get("emoji", "Yes"),
        language=data.get("language", "English"),
    )

    job_id = str(uuid.uuid4())
    with jobs_lock:
        jobs[job_id] = {"status": "pending"}

    threading.Thread(target=_run_calendar_job, args=(job_id, params), daemon=True).start()

    return jsonify({"job_id": job_id, "status": "pending"})


@app.route("/weekly-calendar/status/<job_id>")
def weekly_calendar_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify({"error": "Unknown job_id"}), 404

    return jsonify(job)




@app.route("/download-calendar")
def download_calendar_route():
    if not os.path.exists(CALENDAR_PATH):
        return jsonify({"error": "No calendar has been generated yet. Call /weekly-calendar first."}), 404

    return send_file(
        CALENDAR_PATH,
        as_attachment=True,
        download_name="foodpanda_content_calendar.csv",
    )



@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    full_path = os.path.join(FRONTEND_DIST, path) if path else FRONTEND_DIST
    if path and os.path.exists(full_path) and os.path.isfile(full_path):
        return send_from_directory(FRONTEND_DIST, path)
    # Fallback to index.html for client-side routing (React Router etc.)
    return send_from_directory(FRONTEND_DIST, "index.html")




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
