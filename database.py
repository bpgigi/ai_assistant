import sqlite3

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
            #conn.execute("PRAGMA foreign_keys = ON")
            cursor.execute('''CREATE TABLE IF NOT EXISTS conversations(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL)
            ''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id integer NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            ''')
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
    def add_message(self,conversation_id,role,content):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                insert into messages(conversation_id,role,content) 
                values (?,?,?)""",
                (conversation_id,role,content))
    def get_messages(self,conversation_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                select role,content
                from messages 
                where conversation_id = ?
                order by id''', (conversation_id,))
            rows = cursor.fetchall()
            messages = []
            for role,content in rows:
                messages.append({"role":role,"content":content})
            return messages
    def delete_messages(self,conversation_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            delete from messages where conversation_id = ?''',
            (conversation_id,))
            return cursor.rowcount