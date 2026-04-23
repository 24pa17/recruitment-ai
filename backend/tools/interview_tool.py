import json
from datetime import datetime, timedelta
from services.db import get_connection
from langchain_community.llms import Ollama

llm = Ollama(
    model="mistral:7b",
    base_url="http://49.204.233.77:11434"
)


def normalize_date_value(date_str: str):
    if not date_str:
        return None

    date_str = date_str.strip().lower()

    today = datetime.today().date()

    if date_str == "today":
        return today

    if date_str == "tomorrow":
        return today + timedelta(days=1)

    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def extract_interview_intent(query: str):
    """
    Let the LLM convert the user query into structured JSON.
    """
    prompt = f"""
You are an interview assistant.

Understand the user's query and return ONLY valid JSON in one of these two formats.

If the user wants to schedule an interview:
{{
  "action": "schedule",
  "interviewer_name": "...",
  "candidate_name": "...",
  "job_role": "...",
  "interview_date": "today/tomorrow/DD-MM-YYYY"
}}

If the user wants to list interviews:
{{
  "action": "list",
  "interview_date": "today/tomorrow/DD-MM-YYYY/all"
}}

Rules:
- Return ONLY JSON
- Do not include explanation
- If the query says interviews today, use "today"
- If the query says interviews tomorrow, use "tomorrow"
- If the user asks general interview list, use "all"

User query:
{query}
"""
    try:
        raw = llm.invoke(prompt)
        text = str(raw).strip()

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            return None

        json_text = text[start:end + 1]
        return json.loads(json_text)

    except Exception as e:
        print("❌ LLM extraction error:", str(e))
        return None


def schedule_interview(data: dict) -> str:
    try:
        interview_date = normalize_date_value(data.get("interview_date"))
        if not interview_date:
            return "Could not understand the interview date."

        interviewer_name = (data.get("interviewer_name") or "").strip().title()
        candidate_name = (data.get("candidate_name") or "").strip().title()
        job_role = (data.get("job_role") or "").strip().title()

        if not interviewer_name or not candidate_name or not job_role:
            return "Missing interviewer name, candidate name, or job role."

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO interviews (
                interviewer_name,
                candidate_name,
                interview_date,
                job_role,
                interview_status
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            interviewer_name,
            candidate_name,
            interview_date,
            job_role,
            "Scheduled"
        ))

        interview_id = cur.fetchone()[0]
        conn.commit()

        cur.close()
        conn.close()

        return json.dumps({
            "message": "Interview scheduled successfully",
            "interview_id": interview_id,
            "interviewer_name": interviewer_name,
            "candidate_name": candidate_name,
            "job_role": job_role,
            "interview_date": str(interview_date),
            "interview_status": "Scheduled"
        })

    except Exception as e:
        return f"Error scheduling interview: {str(e)}"


def list_interviews(interview_date_value) -> str:
    try:
        conn = get_connection()
        cur = conn.cursor()

        if interview_date_value == "all":
            cur.execute("""
                SELECT interviewer_name, candidate_name, job_role, interview_date, interview_status
                FROM interviews
                ORDER BY interview_date, id;
            """)
        else:
            cur.execute("""
                SELECT interviewer_name, candidate_name, job_role, interview_date, interview_status
                FROM interviews
                WHERE interview_date = %s
                ORDER BY id;
            """, (interview_date_value,))

        results = cur.fetchall()

        cur.close()
        conn.close()

        interviews = []
        for row in results:
            interviews.append({
                "interviewer_name": row[0],
                "candidate_name": row[1],
                "job_role": row[2],
                "interview_date": str(row[3]),
                "interview_status": row[4]
            })

        return "INTERVIEWS: " + json.dumps(interviews)

    except Exception as e:
        return f"Error fetching interviews: {str(e)}"


def interview_tool(query: str) -> str:
    parsed = extract_interview_intent(query)

    print("📅 Parsed Interview Intent:", parsed)

    if not parsed:
        return "Could not understand the interview request."

    action = parsed.get("action")

    if action == "schedule":
        return schedule_interview(parsed)

    if action == "list":
        raw_date = (parsed.get("interview_date") or "").strip().lower()

        if raw_date == "all":
            return list_interviews("all")

        interview_date = normalize_date_value(raw_date)
        if not interview_date:
            return "Could not understand the interview date."

        return list_interviews(interview_date)

    return "Interview tool could not understand the request."