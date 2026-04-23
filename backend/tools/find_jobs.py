from services.db import get_connection
import json


# =========================
# 🔥 STEP 1: EXTRACT FULL ROLE
# =========================
def extract_role(query: str):
    query = query.lower()

    roles = [
        "python developer",
        "java developer",
        "frontend developer",
        "backend developer",
        "full stack developer",
        "data analyst",
        "data scientist",
        "machine learning engineer",
        "devops engineer",
        "cloud engineer",
        "software tester",
        "qa engineer",
        "ui ux designer",
        "mobile app developer",
        "database administrator",
        "cybersecurity analyst",
        "ai engineer",
        "business analyst",
        "system administrator",
        "network engineer",
        "hr recruiter",
        "product manager",
        "project manager",
        "data engineer",
        "technical support engineer"
    ]

    for role in roles:
        if role in query:
            return role

    return None


# =========================
# 🔥 MAIN TOOL
# =========================
def find_jobs_tool(query: str) -> str:
    try:
        print("🔍 Job Query:", query)

        conn = get_connection()
        cur = conn.cursor()

        # 🔥 Extract role
        role = extract_role(query)

        # =========================
        # 🎯 CASE 1: EXACT ROLE MATCH
        # =========================
        if role:
            print("🎯 Exact role match:", role)

            cur.execute("""
                SELECT title, description, experience_required
                FROM job_openings
                WHERE LOWER(title) = %s
            """, (role,))

        # =========================
        # 📢 CASE 2: FETCH ALL JOBS
        # =========================
        else:
            print("📢 Fetching ALL jobs")

            cur.execute("""
                SELECT title, description, experience_required
                FROM job_openings
                ORDER BY id;
            """)

        results = cur.fetchall()

        print("📊 Raw DB Results:", results)

        cur.close()
        conn.close()

        # 🔴 No results
        if not results:
            return "No job openings found."

        # 🔹 Format response
        jobs = []
        for title, desc, exp in results:
            jobs.append({
                "title": title,
                "description": desc,
                "experience": exp
            })

        print("✅ Final Jobs:", jobs)

        return "JOBS: " + json.dumps(jobs)

    except Exception as e:
        print("❌ Job Tool Error:", str(e))
        return f"Error in find_jobs_tool: {str(e)}"