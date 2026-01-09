import os
import mysql.connector
import json
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conn.cursor(dictionary=True)


model = SentenceTransformer("all-MiniLM-L6-v2")
print(" SentenceTransformer loaded")


cursor.execute("""
    SELECT
        m.restaurant_id,
        m.merged_reviews,
        r.cuisines
    FROM rs_review_merged m
    JOIN restaurants_info r
      ON m.restaurant_id = r.restaurant_id
""")

rows = cursor.fetchall()
print(f" Total restaurants to process: {len(rows)}")

processed = 0

for row in rows:
    restaurant_id = row["restaurant_id"]
    merged_reviews = row["merged_reviews"]
    cuisines = row["cuisines"] or ""

    if not merged_reviews or len(merged_reviews.strip()) < 20:
        continue

    
    final_text = (
        merged_reviews.strip()
        + " cuisines: "
        + cuisines.lower()
    )

    
    embedding_vector = model.encode(final_text).tolist()

    
    cursor.execute("""
        INSERT INTO rs_review_embeddings (restaurant_id, embedding)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
            embedding = VALUES(embedding)
    """, (restaurant_id, json.dumps(embedding_vector)))

    processed += 1

conn.commit()
conn.close()

print(f" COMPLETE: {processed} embeddings stored")
