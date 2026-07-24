import json
import re
import uuid
from pathlib import Path

from flask import (
    Flask,
    abort,
    render_template,
    request,
    send_file
)

from gemini_service import analyze_incident
from report_generator import generate_pdf_report
from utils import allowed_file


app = Flask(__name__)

# Maximum uploaded file size: 2 MB
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024


# Folder used to save temporary analysis data
REPORTS_DIRECTORY = Path("reports")
REPORTS_DIRECTORY.mkdir(exist_ok=True)


def save_analysis_data(analysis, incident, logs, notes):
    """
    Save analysis data as JSON and return a unique report ID.
    """
    report_id = uuid.uuid4().hex

    report_data = {
        "analysis": analysis,
        "incident": incident,
        "logs": logs,
        "notes": notes
    }

    report_path = REPORTS_DIRECTORY / f"{report_id}.json"

    with report_path.open(
        "w",
        encoding="utf-8"
    ) as report_file:
        json.dump(
            report_data,
            report_file,
            ensure_ascii=False,
            indent=2
        )

    return report_id

def load_incident_history():
    """
    Read all saved incident reports and return them as a list.
    """
    history = []

    for report_path in REPORTS_DIRECTORY.glob("*.json"):

        try:
            with report_path.open(
                "r",
                encoding="utf-8"
            ) as report_file:
                report_data = json.load(report_file)

            analysis = report_data.get("analysis", {})
            summary = analysis.get("incident_summary", {})

            root_causes = analysis.get("root_causes", [])

            high_confidence_causes = sum(
            1
            for cause in root_causes
            if str(
            cause.get("confidence", "")
            ).strip().lower() == "high"
            )

            incident_text = report_data.get(
                "incident",
                "No incident description"
            )

            history.append(
    {
        "report_id": report_path.stem,
        "incident": incident_text,
        "status": summary.get(
            "status",
            "Unknown"
        ),
        "impact": summary.get(
            "impact",
            "Unknown"
        ),
        "high_confidence_causes": high_confidence_causes,
        "created_at": report_path.stat().st_mtime
    }
)

        except Exception:
            continue

    history.sort(
        key=lambda item: item["created_at"],
        reverse=True
    )

    return history

def calculate_dashboard_statistics(incident_history):
    """
    Calculate dashboard statistics from saved incidents.
    """

    total_incidents = len(incident_history)
    active_incidents = 0
    resolved_incidents = 0
    high_confidence_causes = 0

    for item in incident_history:

        status = str(
            item.get("status", "")
        ).strip().lower()

        if any(
            word in status
            for word in [
                "resolved",
                "closed",
                "recovered",
                "fixed"
            ]
        ):
            resolved_incidents += 1

        else:
            active_incidents += 1

        high_confidence_causes += item.get(
            "high_confidence_causes",
            0
        )

    return {
        "total_incidents": total_incidents,
        "active_incidents": active_incidents,
        "resolved_incidents": resolved_incidents,
        "high_confidence_causes": high_confidence_causes
    }

@app.route("/", methods=["GET", "POST"])
def home():

    analysis = None
    report_id = ""
    incident = ""
    logs = ""
    notes = ""
    uploaded_filename = ""
    form_error = ""

    if request.method == "POST":

        # Read text fields
        incident = request.form.get("incident", "").strip()
        logs = request.form.get("logs", "").strip()
        notes = request.form.get("notes", "").strip()

        # Read uploaded log file
        uploaded_file = request.files.get("log_file")

        if uploaded_file and uploaded_file.filename:

            uploaded_filename = uploaded_file.filename

            if allowed_file(uploaded_filename):

                try:
                    file_content = uploaded_file.read().decode(
                        "utf-8",
                        errors="replace"
                    ).strip()

                    if logs and file_content:
                        logs = (
                            logs
                            + "\n\n--- Uploaded Log File ---\n"
                            + file_content
                        )

                    elif file_content:
                        logs = file_content

                except Exception:
                    form_error = (
                        "The uploaded log file could not be read."
                    )

            else:
                form_error = (
                    "Unsupported file type. "
                    "Please upload a TXT, LOG, or CSV file."
                )

        # Validate incident information
        if not form_error and not incident and not logs and not notes:
            form_error = (
                "Please enter incident information or upload a log file "
                "before starting the analysis."
            )

        if not form_error:

            try:
                analysis = analyze_incident(
                    incident=incident,
                    logs=logs,
                    notes=notes
                )

                report_id = save_analysis_data(
                    analysis=analysis,
                    incident=incident,
                    logs=logs,
                    notes=notes
                )

            except Exception as error:
                form_error = (
                    "An error occurred while analyzing the incident: "
                    f"{error}"
                )

    incident_history = load_incident_history()

    dashboard_stats = calculate_dashboard_statistics(
    incident_history
    )
    
    return render_template(
    "index.html",
    analysis=analysis,
    report_id=report_id,
    form_error=form_error,
    incident=incident,
    logs=logs,
    notes=notes,
    uploaded_filename=uploaded_filename,
    incident_history=incident_history,
    dashboard_stats=dashboard_stats
)

@app.route("/incident/<report_id>")
def view_incident(report_id):
    """
    Display a previously saved incident analysis.
    """

    if not re.fullmatch(r"[a-f0-9]{32}", report_id):
        abort(404)

    report_path = REPORTS_DIRECTORY / f"{report_id}.json"

    if not report_path.exists():
        abort(404)

    try:
        with report_path.open(
            "r",
            encoding="utf-8"
        ) as report_file:
            report_data = json.load(report_file)

        incident_history = load_incident_history()

        dashboard_stats = calculate_dashboard_statistics(
        incident_history
        )

        return render_template(
            "index.html",
            analysis=report_data.get("analysis", {}),
            report_id=report_id,
            form_error="",
            incident=report_data.get("incident", ""),
            logs=report_data.get("logs", ""),
            notes=report_data.get("notes", ""),
            uploaded_filename="",
            incident_history=incident_history,
            dashboard_stats=dashboard_stats
        )

    except Exception as error:
        return (
            "An error occurred while loading the incident: "
            f"{error}"
        ), 500

@app.route("/download-report/<report_id>")
def download_report(report_id):
    """
    Generate and download the requested PDF report.
    """

    # Only allow valid UUID hexadecimal IDs
    if not re.fullmatch(r"[a-f0-9]{32}", report_id):
        abort(404)

    report_path = REPORTS_DIRECTORY / f"{report_id}.json"

    if not report_path.exists():
        abort(404)

    try:
        with report_path.open(
            "r",
            encoding="utf-8"
        ) as report_file:
            report_data = json.load(report_file)

        pdf_file = generate_pdf_report(
            analysis=report_data.get("analysis", {}),
            incident=report_data.get("incident", ""),
            logs=report_data.get("logs", ""),
            notes=report_data.get("notes", "")
        )

        return send_file(
            pdf_file,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"IncidentIQ_Report_{report_id[:8]}.pdf"
        )

    except Exception as error:
        return (
            "An error occurred while generating the PDF report: "
            f"{error}"
        ), 500


@app.errorhandler(413)
def file_too_large(error):

    return render_template(
        "index.html",
        analysis=None,
        report_id="",
        form_error=(
            "The uploaded file is too large. Maximum size is 2 MB."
        ),
        incident="",
        logs="",
        notes="",
        uploaded_filename=""
    ), 413


if __name__ == "__main__":
    app.run(debug=True)