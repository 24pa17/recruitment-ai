from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import pdfplumber
import psycopg2
import re

app = Flask(__name__)
CORS(app)

# ---------------- CONFIG ----------------
DB_CONFIG = {
    "dbname": "mfrp_sneha",
    "user": "dbadmin",
    "password": "Ur12ec125",
    "host": "49.204.233.77",
    "port": "5432"
}

OLLAMA_URL = "http://49.204.233.77:11434/api/chat"
EMBED_URL = "http://49.204.233.77:11434/api/embeddings"

# ---------------- EMBEDDING ----------------
def get_embedding(text):
    res = requests.post(EMBED_URL, json={
        "model": "nomic-embed-text",
        "prompt": text
    })
    data = res.json()

    if "embedding" not in data:
        raise Exception(f"Embedding failed: {data}")

    return data["embedding"]

# ---------------- LLM ----------------
def call_llm(prompt):
    try:
        res = requests.post(OLLAMA_URL, json={
            "model": "mistral",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        })
        data = res.json()

        if "message" in data:
            return data["message"].get("content", "")
        elif "response" in data:
            return data["response"]
        elif "error" in data:
            return f"Error: {data['error']}"
        return ""

    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- QUERY TYPE ----------------
def is_job_query(text):
    keywords = ["candidate", "job", "hire", "developer", "engineer", "role"]
    return any(word in text.lower() for word in keywords)

# ---------------- UPLOAD RESUME ----------------
@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"})

        file = request.files["file"]

        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t

        if not text.strip():
            return jsonify({"error": "No text found in resume"})

        # Basic extraction
        name = text.split("\n")[0]
        email_match = re.search(r"\S+@\S+", text)
        email = email_match.group() if email_match else ""

        # ✅ CLEAN EMBEDDING (NO MANUAL SKILLS)
        combined = f"{name}. Resume: {text[:2000]}"
        embedding = get_embedding(combined)

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Insert candidate
        cur.execute(
            "INSERT INTO candidates (name, email) VALUES (%s, %s) RETURNING id;",
            (name, email)
        )
        cid = cur.fetchone()[0]

        # Insert embedding
        cur.execute(
            "INSERT INTO candidate_chunks (candidate_id, chunk_text, embedding) VALUES (%s, %s, %s)",
            (cid, combined, embedding)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Resume uploaded successfully", "name": name})

    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------- CHAT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() if request.is_json else request.form
        user_msg = data.get("message", "")

        # -------- JOB QUERY --------
        if is_job_query(user_msg):

            # 1️⃣ Convert query to embedding
            query_embedding = get_embedding(user_msg)
            emb_str = str(query_embedding)

            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            # 2️⃣ Vector similarity search
            cur.execute(f"""
                SELECT c.name, cc.chunk_text,
                       cc.embedding <-> '{emb_str}' AS distance
                FROM candidate_chunks cc
                JOIN candidates c ON cc.candidate_id = c.id
                ORDER BY distance
                LIMIT 5;
            """)

            results = cur.fetchall()
            cur.close()
            conn.close()

            if not results:
                return jsonify({"reply": "No candidates found."})

            # 3️⃣ Build context
            context = ""
            for r in results:
                name, text, dist = r
                context += f"Candidate: {name}\n{text}\n\n"

            # 4️⃣ LLM handles everything
            rag_prompt = f"""
You are an intelligent AI recruitment assistant.

User Query:
{user_msg}

Candidate Data:
{context}

Format the response in clean Markdown.

### Job Role
<role>

### Required Skills
- skill 1
- skill 2
- skill 3

### Top Candidates

#### 1. <Name>
**Matching Skills:**
- skill
- skill

**Reason:**
Short explanation.

#### 2. <Name>
**Matching Skills:**
- skill
- skill

**Reason:**
Short explanation.

Keep it neat, readable, and professional.
"""

            answer = call_llm(rag_prompt)

            return jsonify({"reply": answer})

        # -------- GENERAL CHAT --------
        else:
            answer = call_llm(user_msg)
            return jsonify({"reply": answer})

    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)