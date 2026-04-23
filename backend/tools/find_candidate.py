from services.embedding import get_embedding
from services.db import get_connection
import json
import re


def find_candidate_tool(query: str) -> str:
    try:
        print("🔍 Query:", query)

        query_lower = query.lower()

        # 🔹 Step 1: Keyword extraction
        skill_list = [
            "python", "java", "sql", "machine learning", "data",
            "react", "node"
        ]

        domain_keywords = ["physics", "chemistry", "tamil", "math"]
        role_keywords = ["professor", "assistant professor", "lecturer"]

        keywords = []

        for skill in skill_list:
            if skill in query_lower:
                keywords.append(skill)

        for domain in domain_keywords:
            if domain in query_lower:
                keywords.append(domain)

        for role in role_keywords:
            if role in query_lower:
                keywords.append(role)

        if keywords:
            keyword_filter = "%" + "%".join(keywords) + "%"
        else:
            keyword_filter = f"%{query}%"

        # 🔹 Step 2: Embedding
        query_embedding = get_embedding(query)
        emb_str = "[" + ",".join(map(str, query_embedding)) + "]"

        # 🔹 Step 3: DB
        conn = get_connection()
        cur = conn.cursor()

        # 🔹 Step 4: Hybrid search
        cur.execute("""
            SELECT DISTINCT ON (c.id)
                c.name,
                cc.chunk_text,
                cc.embedding <-> %s::vector AS distance
            FROM candidate_chunks cc
            JOIN candidates c ON cc.candidate_id = c.id
            WHERE cc.chunk_text ILIKE %s
              AND cc.embedding <-> %s::vector < 0.4
            ORDER BY c.id, distance ASC
            LIMIT 5;
        """, (emb_str, keyword_filter, emb_str))

        results = cur.fetchall()

        # 🔹 Step 5: Fallback
        if not results:
            cur.execute("""
                SELECT DISTINCT ON (c.id)
                    c.name,
                    cc.chunk_text,
                    cc.embedding <-> %s::vector AS distance
                FROM candidate_chunks cc
                JOIN candidates c ON cc.candidate_id = c.id
                ORDER BY c.id, distance ASC
                LIMIT 5;
            """, (emb_str,))
            results = cur.fetchall()

        cur.close()
        conn.close()

        # 🔹 Step 6: No results
        if not results:
            return "No suitable candidates found. Try refining the role or skills."

        # 🔥 Step 7: CLEAN SKILLS (IMPORTANT FIX)
        clean_results = []
        seen_names = set()

        for name, text, distance in results:
            if name not in seen_names:

                # 🔹 Clean raw text
                cleaned = re.sub(r'[\n/|]', ',', text)

                # 🔹 Split + trim
                skills = [s.strip() for s in cleaned.split(",") if len(s.strip()) > 2]

                # 🔹 Remove duplicates
                skills = list(dict.fromkeys(skills))

                # 🔹 Limit top 5
                skills = skills[:5]

                clean_results.append({
                    "name": name,
                    "skills": skills,
                    "score": round(1 / (1 + distance), 3)
                })

                seen_names.add(name)

        # 🔹 Step 8: Sort
        clean_results = sorted(clean_results, key=lambda x: x["score"], reverse=True)

        print("✅ Results:", clean_results)

        return f"CANDIDATES: {json.dumps(clean_results)}"

    except Exception as e:
        return f"Error in find_candidate_tool: {str(e)}"