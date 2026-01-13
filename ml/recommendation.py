
import os
import re
import json
import numpy as np
import mysql.connector
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def extract_city(cursor, text):
    text = text.lower()
    cursor.execute("SELECT DISTINCT city FROM restaurants_info WHERE city IS NOT NULL")
    cities = [r["city"].lower() for r in cursor.fetchall()]
    for c in cities:
        if c in text:
            return c
    return None


def extract_cuisine(cursor, text):
    text = text.lower()
    cursor.execute("SELECT DISTINCT cuisines FROM restaurants_info WHERE cuisines IS NOT NULL")
    rows = cursor.fetchall()

    cuisine_set = set()
    for r in rows:
        for c in r["cuisines"].split(","):
            cuisine_set.add(c.strip().lower())

    for c in cuisine_set:
        if c in text:
            return c
    return None

'''
def extract_price(text):
    text = text.lower()

    # explicit number
    m = re.search(r'\b(\d{3,5})\b', text)
    if m:
        return int(m.group(1))

    # intent words
    if any(w in text for w in ["cheap", "budget", "low"]):
        return 1500
    if any(w in text for w in ["expensive", "premium", "luxury", "high"]):
        return 4000

    return None'''


def extract_rating_filter(text):
    text = text.lower()

    # 1–5 ke beech rating
    m = re.search(r'\b([1-5](?:\.\d)?)\b', text)
    if not m:
        if any(w in text for w in ["best", "top", "excellent"]):
            return ("gte", 4.0)
        return None, None

    rating= float(m.group(1))

    if any(w in text for w in ["above", "greater", "more than", "over"]):
        return ("gt", rating)

    if any(w in text for w in ["below", "less than", "under"]):
        return ("lt", rating)

    return ("gte", rating)




def get_recommendations(user_text):

    model = SentenceTransformer("all-MiniLM-L6-v2")
    user_embedding = model.encode(user_text)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    
    # INTENT EXTRACTION
   
    city = extract_city(cursor, user_text)
    cuisine = extract_cuisine(cursor, user_text)
    # price = extract_price(user_text)
    rating_op, rating_value = extract_rating_filter(user_text)
    has_structured_signal = any([city, cuisine, rating_op])

    
    # FILTER restaurants_info
    
    query = "SELECT * FROM restaurants_info WHERE 1=1"
    params = []

    if city:
        query += " AND LOWER(city) = %s"
        params.append(city)

    if cuisine:
        query += " AND LOWER(cuisines) LIKE %s"
        params.append(f"%{cuisine}%")

   # if price:
    #    query += " AND cost_for_two <= %s"
    #    params.append(price)

    if rating_op and rating_value:
        if rating_op == "gt":
            query += " AND rating > %s"
        elif rating_op == "lt":
            query += " AND rating < %s"
        else:  # gte
            query += " AND rating >= %s"
        params.append(rating_value)

    cursor.execute(query, params)
    restaurants = cursor.fetchall()

    if not restaurants:
        conn.close()
        return {"results": {}}
 
    # SEMANTIC SCORING
   
    scored = []
    max_similarity = 0.0

    for r in restaurants:
        cursor.execute(
            "SELECT merged_reviews FROM rs_review_merged WHERE restaurant_id = %s",
            (r["restaurant_id"],)
        )
        row = cursor.fetchone()
        if not row or not row["merged_reviews"]:
            continue

        cursor.execute(
            "SELECT embedding FROM rs_review_embeddings WHERE restaurant_id = %s",
            (r["restaurant_id"],)
        )
        emb_row = cursor.fetchone()
        if not emb_row:
            continue

        review_embedding = np.array(json.loads(emb_row["embedding"]))
        similarity = cosine_similarity(
            [user_embedding],
            [review_embedding]
        )[0][0]

        max_similarity = max(max_similarity, similarity)

        final_score = (
            0.4 * similarity +
            0.3 * (r["rating"] / 5 if r["rating"] else 0) +
            0.3 * 1
        )

        scored.append({
        "id": r["restaurant_id"],     
        "name": r["name"],
        "image": r["image_url"],      
        "cuisines": r["cuisines"],    
        "locality": r["locality"],    
        "city": r["city"],
        "rating": r["rating"],
        "score": round(final_score, 3)
})

    conn.close()

    if not scored:
        return {"results": {}}

    scored.sort(key=lambda x: x["score"], reverse=True)

    
    SEMANTIC_THRESHOLD = 0.35
    search_mode = has_structured_signal or max_similarity >= SEMANTIC_THRESHOLD

    final = {}

    if search_mode:
        if city:
            final[city.capitalize()] = scored[:3]
        else:
            for r in scored:
                final.setdefault(r["city"], []).append(r)
            for c in final:
                final[c] = final[c][:3]
    else:
        city_map = {}
        for r in scored:
            city_map.setdefault(r["city"], []).append(r)
        for c in city_map:
            final[c] = city_map[c][:3]

    return {"results": final}
