# core/db.py
import sqlite3
from typing import List, Optional, Tuple
from datetime import datetime
from config import DB_PATH

def get_conn():
    return sqlite3.connect(DB_PATH)

def ensure_schema():
    conn = get_conn()
    c = conn.cursor()
    # conversations (you already have it, keep same columns)
    c.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT,
        ai_output TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        message_type TEXT DEFAULT 'text'
    )
    """)
    c.execute("INSERT INTO knowledge (question, answer, tags) VALUES (?,?,?)",
          ("Who is Pablo Escobar?", "Pablo Escobar was a Colombian drug lord who led the Medellín Cartel.", "history,crime,Colombia"))
    conn.commit()

    # offline knowledge (Q&A or snippets)
    c.execute("""
    CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT,
        tags TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def save_conversation(user_input: str, ai_output: str, message_type: str="text"):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO conversations (user_input, ai_output, message_type)
        VALUES (?, ?, ?)
    """, (user_input, ai_output, message_type))
    conn.commit()
    conn.close()

def search_knowledge(query: str) -> Optional[str]:
    conn = get_conn()
    c = conn.cursor()
    # simple LIKE; replace with FTS later
    c.execute("""
        SELECT answer FROM knowledge
        WHERE question LIKE ? OR tags LIKE ?
        ORDER BY id DESC LIMIT 1
    """, (f"%{query}%", f"%{query}%"))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def upsert_knowledge(question: str, answer: str, tags: str=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO knowledge (question, answer, tags)
        VALUES (?, ?, ?)
    """, (question, answer, tags))
    conn.commit()
    conn.close()

def recent_messages(limit: int=10) -> List[Tuple]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT user_input, ai_output, timestamp FROM conversations
        ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
