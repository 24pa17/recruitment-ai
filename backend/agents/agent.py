import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

from tools.find_candidate import find_candidate_tool
from tools.find_jobs import find_jobs_tool
from tools.interview_tool import interview_tool

llm = Ollama(
    model="mistral:7b",
    base_url="http://49.204.233.77:11434"
)

intent_prompt = PromptTemplate.from_template("""
Classify the user query into ONE of these:
- recruitment
- job_opening
- interview
- general

Rules:
- If user asks about candidates → recruitment
- If user asks about job openings, jobs, roles → job_opening
- If user asks to schedule interview or list interviews → interview
- Otherwise → general

Query: {query}

Answer only one word.
""")

intent_chain = LLMChain(llm=llm, prompt=intent_prompt)

extract_prompt = PromptTemplate.from_template("""
Extract job title and required skills.

Query: {query}

Return JSON:
{{
  "job_title": "...",
  "required_skills": ["...", "..."]
}}
""")

extract_chain = LLMChain(llm=llm, prompt=extract_prompt)


def run_agent(query: str):
    try:
        intent = intent_chain.run({"query": query}).strip().lower()
        print("🧠 Intent:", intent)

        if intent == "general":
            response = llm.invoke(query)
            return {
                "type": "text",
                "reply": str(response)
            }

        elif intent == "job_opening":
            job_result = find_jobs_tool(query)
            print("📢 Job Tool Output:", job_result)

            if job_result.startswith("JOBS:"):
                try:
                    jobs = json.loads(job_result.replace("JOBS: ", ""))
                    return {
                        "type": "job_list",
                        "jobs": jobs
                    }
                except Exception as e:
                    print("❌ Job JSON parse error:", e)
                    return {
                        "type": "text",
                        "reply": "Error reading job data"
                    }

            return {
                "type": "text",
                "reply": job_result
            }

        elif intent == "interview":
            result = interview_tool(query)
            print("📅 Interview Tool Output:", result)

            if result.startswith("INTERVIEWS:"):
                try:
                    interviews = json.loads(result.replace("INTERVIEWS: ", ""))
                    return {
                        "type": "interview_list",
                        "interviews": interviews
                    }
                except Exception as e:
                    print("❌ Interview JSON parse error:", e)
                    return {
                        "type": "text",
                        "reply": "Error reading interview data"
                    }

            try:
                structured_result = json.loads(result)
                return {
                    "type": "text",
                    "reply": structured_result.get("message", "Interview updated.")
                }
            except Exception:
                return {
                    "type": "text",
                    "reply": result
                }

        elif intent == "recruitment":
            structured = extract_chain.run({"query": query})

            try:
                structured_json = json.loads(structured)
            except Exception:
                print("⚠️ JSON parse failed:", structured)
                structured_json = {
                    "job_title": query,
                    "required_skills": []
                }

            tool_result = find_candidate_tool(query)
            print("👨‍💻 Candidate Tool Output:", tool_result)

            if "No suitable candidates" in tool_result:
                return {
                    "type": "job_result",
                    "job_title": structured_json["job_title"],
                    "required_skills": structured_json["required_skills"],
                    "candidates": []
                }

            if tool_result.startswith("CANDIDATES:"):
                try:
                    candidates = json.loads(tool_result.replace("CANDIDATES: ", ""))
                    return {
                        "type": "job_result",
                        "job_title": structured_json["job_title"],
                        "required_skills": structured_json["required_skills"],
                        "candidates": candidates
                    }
                except Exception as e:
                    print("❌ Candidate JSON parse error:", e)
                    return {
                        "type": "text",
                        "reply": "Error reading candidate data"
                    }

            return {
                "type": "text",
                "reply": tool_result
            }

        return {
            "type": "text",
            "reply": "I didn't understand your request. Please try again."
        }

    except Exception as e:
        print("❌ AGENT ERROR:", str(e))
        return {
            "type": "text",
            "reply": f"Error: {str(e)}"
        }