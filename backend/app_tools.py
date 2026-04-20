#embedding resume
from langchain_community.vectorstores import PGVector
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

CONNECTION_STRING = "postgresql+psycopg2://dbadmin:Ur12ec125@49.204.233.77:5432/mfrp_sneha"
COLLECTION_NAME = "candidates"
OLLAMA_URL = "http://49.204.233.77:11434"

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=OLLAMA_URL
)

def ingest_resume(text, name):

    skills_list = [
        "python", "java", "sql", "machine learning",
        "deep learning", "react", "node", "html", "css"
    ]

    found_skills = [s for s in skills_list if s in text.lower()]

    doc = Document(
        page_content=text,
        metadata={
            "name": name,
            "skills": found_skills
        }
    )

    PGVector.from_documents(
        documents=[doc],
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING
    )


    #candidates

import re
import json
from langchain_community.vectorstores import PGVector
from langchain_ollama import OllamaEmbeddings, ChatOllama

CONNECTION_STRING = "postgresql+psycopg2://dbadmin:Ur12ec125@49.204.233.77:5432/mfrp_sneha"
COLLECTION_NAME = "candidates"
OLLAMA_URL = "http://49.204.233.77:11434"

embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_URL)
llm = ChatOllama(model="mistral", base_url=OLLAMA_URL, temperature=0)

db = PGVector(
    connection_string=CONNECTION_STRING,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings
)

def extract_role_and_skills(query):
    prompt = f"""
Extract job role and skills.

Query: {query}

Return JSON:
{{
 "role": "",
 "skills": []
}}
"""
    res = llm.invoke(prompt).content

    match = re.search(r"\{.*\}", res, re.DOTALL)

    if match:
        data = json.loads(match.group())
        role = data.get("role", "")
        skills = data.get("skills", [])

        if not skills:
            skills = query.lower().split()

        return role, skills

    return query, query.lower().split()


def search_candidates(query):

    role, skills = extract_role_and_skills(query)

    docs = db.similarity_search(query, k=10)

    filtered = []

    for d in docs:
        doc_skills = d.metadata.get("skills", [])

        if any(skill.lower() in doc_skills for skill in skills):
            filtered.append(d)

    if not filtered:
        filtered = docs[:3]

    context = "\n\n".join([
        f"{d.metadata['name']} | Skills: {d.metadata['skills']}\n{d.page_content}"
        for d in filtered
    ])

    prompt = f"""
You are an AI recruitment assistant.

Role: {role}
Required Skills: {skills}

Candidates:
{context}

Give:
1. Best candidates
2. Score (0-100)
3. Why they are suitable
"""

    return llm.invoke(prompt).content

#main
from flask import Flask, request, jsonify
import pdfplumber

from embed_resume import ingest_resume
from rag_candidates import search_candidates
from langchain_ollama import ChatOllama

app = Flask(__name__)

llm = ChatOllama(
    model="mistral",
    base_url="http://49.204.233.77:11434"
)


def is_job_query(q):
    return any(x in q.lower() for x in [
        "candidate", "hire", "developer", "engineer", "job"
    ])


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
            return jsonify({"error": "Empty resume"})

        name = text.split("\n")[0]

        ingest_resume(text, name)

        return jsonify({
            "message": "Resume uploaded successfully",
            "name": name
        })

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")

    if is_job_query(user_msg):
        answer = search_candidates(user_msg)
    else:
        answer = llm.invoke(user_msg).content

    return jsonify({"reply": answer})


if __name__ == "__main__":
    app.run(debug=True)

