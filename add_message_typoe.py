import sqlite3

DB_FILE = "raya_conversation.db"

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# Check if column exists
c.execute("PRAGMA table_info(conversations)")
columns = [col[1] for col in c.fetchall()]

if "message_type" not in columns:
    c.execute("ALTER TABLE conversations ADD COLUMN message_type TEXT DEFAULT 'text'")
    print("✅ Column 'message_type' added.")
else:
    print("ℹ️ Column 'message_type' already exists.")

conn.commit()
conn.close()