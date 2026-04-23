from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.agent import run_agent
from services.resume_parser import extract_text
from services.store_candidate import store_candidate

app = Flask(__name__)
CORS(app)

# =========================
# 💬 CHAT API
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_msg = data.get("message", "").strip()

    print("📩 USER:", user_msg)

    if not user_msg:
        return jsonify({
            "type": "text",
            "reply": "Message is required."
        }), 400

    try:
        response = run_agent(user_msg)

        print("🤖 RESPONSE:", response)

        # If response is plain string, wrap it
        if isinstance(response, str):
            return jsonify({
                "type": "text",
                "reply": response
            }), 200

        return jsonify(response), 200

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({
            "type": "text",
            "reply": f"Server error: {str(e)}"
        }), 500


# =========================
# 📄 RESUME UPLOAD API
# =========================
@app.route("/upload", methods=["POST"])
def upload_resume():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if not file or not file.filename.strip():
            return jsonify({"error": "Invalid file"}), 400

        print("📄 Uploading file:", file.filename)

        # 🔹 Extract text
        text = extract_text(file)

        if not text or not text.strip():
            return jsonify({"error": "Could not extract text from file"}), 400

        print("📃 Extracted text length:", len(text))

        # 🔹 Store in DB
        result = store_candidate(text)

        print("✅ Stored candidate:", result)

        return jsonify(result), 200

    except Exception as e:
        print("❌ UPLOAD ERROR:", str(e))
        return jsonify({
            "error": str(e)
        }), 500


# =========================
# 🚀 START SERVER
# =========================
if __name__ == "__main__":
    print("🚀 Server starting...")
    app.run(debug=True)