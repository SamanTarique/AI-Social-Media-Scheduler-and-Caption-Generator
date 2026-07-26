from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os

from Gemni_Services import generate_caption
from Ai_Scheduler_Caption_Generator import build_weekly_calendar, save_calendar

app = Flask(__name__)
CORS(app)

CALENDAR_PATH = "output/foodpanda_content_calendar.csv"

@app.route("/")
def home():
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


@app.route("/weekly-calendar", methods=["POST"])
def weekly_calendar_route():
    data = request.get_json(force=True) or {}

    rows = build_weekly_calendar(
        market=data.get("market", "Pakistan"),
        platform=data.get("platform", "Instagram"),
        start_date=data.get("start_date"),
        goal=data.get("goal", "Increase Engagement"),
        audience=data.get("audience", "Students"),
        emoji=data.get("emoji", "Yes"),
        language=data.get("language", "English"),
    )

    save_calendar(rows, path=CALENDAR_PATH)

    return jsonify({"calendar": rows})


@app.route("/download-calendar")
def download_calendar_route():
    if not os.path.exists(CALENDAR_PATH):
        return jsonify({"error": "No calendar has been generated yet. Call /weekly-calendar first."}), 404

    return send_file(
        CALENDAR_PATH,
        as_attachment=True,
        download_name="foodpanda_content_calendar.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)
