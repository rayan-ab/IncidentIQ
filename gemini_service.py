from google import genai
from dotenv import load_dotenv
import json
import os


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def analyze_incident(incident, logs, notes):

    prompt = f"""
You are an AI-powered incident response and root-cause analysis assistant.

Analyze the following software incident carefully.

Incident Description:
{incident if incident else "Not provided"}

Application Logs:
{logs if logs else "Not provided"}

Deployment Notes:
{notes if notes else "Not provided"}

Return ONLY valid JSON.

Do not add Markdown code fences.
Do not write any text before or after the JSON.

Use exactly this structure:

{{
  "incident_summary": {{
    "description": "Short description of the incident",
    "status": "Current incident status or Unknown",
    "impact": "Likely impact of the incident"
  }},
  "timeline": [
    {{
      "timestamp": "Timestamp or Unknown",
      "event": "Description of the event"
    }}
  ],
  "root_causes": [
    {{
      "title": "Short hypothesis title",
      "explanation": "Explanation of the possible root cause",
      "confidence": "High, Medium, or Low"
    }}
  ],
  "evidence": [
    "Fact directly supported by the provided data"
  ],
  "assumptions": [
    "Assumption made during analysis"
  ],
  "uncertainties": [
    "Missing or uncertain information"
  ],
  "immediate_actions": [
    "Prioritized immediate action"
  ],
  "long_term_actions": [
    "Recommended long-term improvement"
  ]
}}

Important rules:

- Clearly distinguish facts from hypotheses.
- Do not invent logs, timestamps, technical details, or system behavior.
- Use "Unknown" when information is unavailable.
- Evidence must contain only facts supported by the supplied data.
- Root causes must be presented as unconfirmed hypotheses.
- Confidence must be High, Medium, or Low.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    raw_response = response.text

    if not raw_response:
        raise ValueError("Gemini returned an empty response.")

    cleaned_response = raw_response.strip()

    # Remove Markdown fences if Gemini adds them accidentally
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:]

    elif cleaned_response.startswith("```"):
        cleaned_response = cleaned_response[3:]

    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]

    cleaned_response = cleaned_response.strip()

    try:
        return json.loads(cleaned_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Gemini returned an invalid JSON response."
        ) from error