from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_ollama import OllamaLLM

app = Flask(__name__)
CORS(app)

llm = OllamaLLM(
    model="mistral:7b",
    base_url="http://49.204.233.77:11434"
)

# 🔑 KEYWORDS
RECRUITMENT_KEYWORDS = [
    "job", "candidate", "resume", "interview",
    "hiring", "skills", "hr", "recruitment", "position"
]

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_msg = request.json.get("message", "")
        lower_msg = user_msg.lower()

        print("User:", user_msg)

        # 🔥 CHECK TYPE
        is_recruitment = any(word in lower_msg for word in RECRUITMENT_KEYWORDS)

        # ✅ CASE 1: Recruitment Query
        if is_recruitment:
            prompt = f"""
You are an AI Recruitment Assistant.

Answer professionally related to:
- job openings
- candidates
- interviews
- HR process

User question: {user_msg}
"""

        # ✅ CASE 2: General Query
        else:
            prompt = user_msg   # normal AI response

        response = llm.invoke(prompt)

        return jsonify({
            "reply": response
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "reply": "Error from AI system"
        })

if __name__ == "__main__":
    app.run(debug=True)