import sqlite3
import json

class Database:
    def __init__(self,db_name = "assistant.db"):
        self.db_name = db_name
        self.create_tables()
    def connect(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                   CREATE TABLE IF NOT EXISTS conversations
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       title TEXT NOT NULL
                   )
                """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS messages
                           (
                               id INTEGER PRIMARY KEY AUTOINCREMENT, 
                               conversation_id INTEGER NOT NULL,
                               role TEXT NOT NULL,
                               content TEXT NOT NULL,
                               sources TEXT NOT NULL DEFAULT '[]',
                               FOREIGN KEY ( conversation_id)    
                                     REFERENCES conversations(id)
                               ON DELETE CASCADE)  
                           """)

            # 检查现有 messages 表有哪些字段
            cursor.execute("PRAGMA table_info(messages)")
            columns = [
                row[1]
                for row in cursor.fetchall()
            ]

            # 旧数据库缺少 sources 时，自动添加
            if "sources" not in columns:
                cursor.execute("""
                               ALTER TABLE messages
                                   ADD COLUMN sources TEXT NOT NULL DEFAULT '[]'
                               """)

    def create_conversation(self,title):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                insert into conversations(title) values (?)''',
                (title,)
                )
            #返回刚刚插入的那条数据的 id。
            return cursor.lastrowid
    def get_conversations(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''select id,title from conversations order by id desc ''')
            return cursor.fetchall()
    def get_conversation(self,conversation_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            select id,title from conversations where id = ?''',
                           (conversation_id,))
            return cursor.fetchone()
    def delete_conversation(self,conversation_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("delete from conversations where id = ?",(conversation_id,))
            return cursor.rowcount

    def add_message(self, conversation_id, role, content, sources=None):
        if sources is None:
            sources = []

        sources_json = json.dumps(sources, ensure_ascii=False)

        with self.connect() as conn:
            conn.execute("""
                         INSERT INTO messages(conversation_id, role, content, sources)
                         VALUES (?, ?, ?, ?)
                         """, (conversation_id, role, content, sources_json))

    def get_messages(self, conversation_id):
        with self.connect() as conn:
            cursor = conn.execute("""
                                  SELECT role, content, sources
                                  FROM messages
                                  WHERE conversation_id = ?
                                  ORDER BY id
                                  """, (conversation_id,))

            rows = cursor.fetchall()
            messages = []

            for role, content, sources_json in rows:
                messages.append({
                    "role": role,
                    "content": content,
                    "sources": json.loads(sources_json)
                })

            return messages
    def delete_messages(self,conversation_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            delete from messages where conversation_id = ?''',
            (conversation_id,))
            return cursor.rowcount