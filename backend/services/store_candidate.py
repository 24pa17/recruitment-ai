from services.embedding import get_embedding
from services.db import get_connection


def split_text(text, chunk_size=300):
    words = text.split()
    return [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]


def extract_basic_info(text):
    lines = text.split("\n")

    name = lines[0][:100] if lines else "Unknown"
    email = "unknown@email.com"

    for line in lines:
        if "@" in line:
            email = line.strip()
            break

    return name, email


def store_candidate(text):
    conn = get_connection()
    cur = conn.cursor()

    # 🔹 Extract name + email
    name, email = extract_basic_info(text)

    # 🔹 Insert candidate
    cur.execute("""
        INSERT INTO candidates (name, email, age, experience_years)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (name, email, 0, 0))

    candidate_id = cur.fetchone()[0]

    # 🔹 Split resume into chunks
    chunks = split_text(text)

    for chunk in chunks:
        embedding = get_embedding(chunk)

        emb_str = "[" + ",".join(map(str, embedding)) + "]"

        cur.execute("""
            INSERT INTO candidate_chunks (candidate_id, chunk_text, embedding)
            VALUES (%s, %s, %s::vector);
        """, (candidate_id, chunk, emb_str))

    conn.commit()
    cur.close()
    conn.close()

    return {
        "message": "Candidate stored successfully",
        "candidate_id": candidate_id
    }