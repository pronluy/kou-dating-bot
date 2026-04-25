from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

DATABASE_URL = "postgresql://neondb_owner:npg_KB5WCm3wvGHU@ep-wild-sea-aoi12454.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

class UserCreate(BaseModel):
    tg_id: int
    full_name: str
    age: int
    gender: str
    looking_for: str
    city: str
    country: str
    lang: str = "kh"
    photo_url: str
    bio: Optional[str] = ""
    referred_by: Optional[int] = None

class ActionModel(BaseModel):
    from_id: int
    to_id: int
    action: str

class PreferenceUpdate(BaseModel):
    tg_id: int
    preference: str
    search_city: str = None

class LangUpdate(BaseModel):
    tg_id: int
    lang: str

def get_db_conn():
    return psycopg2.connect(DATABASE_URL)

@app.get("/")
def home():
    return {"message": "KOU Dating API is Running"}

@app.post("/register")
def register_user(user: UserCreate):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        
        cur.execute("SELECT telegram_id FROM users WHERE telegram_id = %s;", (user.tg_id,))
        if cur.fetchone():
            update_query = """
                UPDATE users SET 
                full_name=%s, age=%s, gender=%s, looking_for=%s, city=%s, country=%s, language=%s, photo_url=%s, bio=%s
                WHERE telegram_id=%s;
            """
            cur.execute(update_query, (user.full_name, user.age, user.gender, user.looking_for, user.city, user.country, user.lang, user.photo_url, user.bio, user.tg_id))
        else:
            insert_query = """
                INSERT INTO users (telegram_id, full_name, age, gender, looking_for, city, country, language, photo_url, bio, referred_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cur.execute(insert_query, (user.tg_id, user.full_name, user.age, user.gender, user.looking_for, user.city, user.country, user.lang, user.photo_url, user.bio, user.referred_by))
            
            if user.referred_by:
                cur.execute("UPDATE users SET referral_count = COALESCE(referral_count, 0) + 1 WHERE telegram_id = %s;", (user.referred_by,))
            
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/profile/{tg_id}")
def get_profile(tg_id: int):
    try:
        conn = get_db_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE telegram_id = %s;", (tg_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if not user: raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/profile/{tg_id}")
def delete_profile(tg_id: int):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM interactions WHERE from_id = %s OR to_id = %s;", (tg_id, tg_id))
        cur.execute("DELETE FROM users WHERE telegram_id = %s;", (tg_id,))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/preference")
def update_preference(req: PreferenceUpdate):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("UPDATE users SET search_preference = %s, search_city = %s WHERE telegram_id = %s;", 
                    (req.preference, req.search_city, req.tg_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/language")
def update_language(req: LangUpdate):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("UPDATE users SET language = %s WHERE telegram_id = %s;", (req.lang, req.tg_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/match/{tg_id}")
def get_match(tg_id: int):
    try:
        conn = get_db_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE telegram_id = %s;", (tg_id,))
        me = cur.fetchone()
        
        if not me:
            cur.close()
            conn.close()
            return {"status": "no_user"}

        pref = me.get('search_preference') or 'local'
        target_city = me.get('search_city')

        query = """
            SELECT * FROM users 
            WHERE gender = %s AND looking_for = %s AND telegram_id != %s 
            AND telegram_id NOT IN (SELECT to_id FROM interactions WHERE from_id = %s)
        """
        params = [me['looking_for'], me['gender'], tg_id, tg_id]

        if pref == 'local':
            query += " AND city = %s"
            params.append(me['city'])
        elif pref == 'specific' and target_city:
            query += " AND city = %s"
            params.append(target_city)

        query += " ORDER BY RANDOM() LIMIT 1;"
        
        cur.execute(query, tuple(params))
        match = cur.fetchone()
        cur.close()
        conn.close()
        
        if not match: return {"status": "no_match"}
        return {"status": "success", "match": match}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/interact")
def interact_user(req: ActionModel):
    try:
        conn = get_db_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO interactions (from_id, to_id, action) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (from_id, to_id) DO NOTHING
        """, (req.from_id, req.to_id, req.action))
        
        is_match = False
        if req.action == 'like':
            cur.execute("SELECT * FROM interactions WHERE from_id = %s AND to_id = %s AND action = 'like';", (req.to_id, req.from_id))
            if cur.fetchone(): is_match = True
                
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "is_match": is_match}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)