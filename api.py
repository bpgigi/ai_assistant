from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import sqlite3

def get_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    with get_connection() as conn:
        #cursor = conn.cursor()
        conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            chinese INTEGER NOT NULL,
            math INTEGER NOT NULL,
            english INTEGER NOT NULL)""")
init_db()
app = FastAPI()
@app.get("/")
def root():
    return {"message": "你好，FastaAPI"}

class Student(BaseModel):
    name: str
    chinese:int
    math: int
    english:int

@app.post("/students")
def add_student(student: Student):
    conn = get_connection()
    cursor = conn.execute("""
        insert into students(name,chinese,math,english)
                    values(?,?,?,?)""",
    (student.name,student.chinese,student.math,student.english))
    conn.commit()
    student_id = cursor.lastrowid
    conn.close()
    return {
        "id": student_id,
        "name": student.name,
        "chinese": student.chinese,
        "math": student.math,
        "english": student.english
    }

@app.get("/students")
def get_students():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/students/{studens_id}")
def get_student(studens_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM students WHERE id = ?",
                       (studens_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return dict(row)

@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    conn = get_connection()
    cursor = conn.execute("""
    update students
    set name = ?,chinese = ?,math = ?,english = ?
        where id = ?""",
                          (student.name,
                           student.chinese,
                           student.math,
                           student.english,
                           student_id))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404,detail="没这入")
    return {
        "id": student_id,
        "name": student.name,
        "chinese":student.chinese,
        "math":student.math,
        "english":student.english
    }

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_connection()
    cursor = conn.execute("""
    delete from students where id = ?""",(student_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404,detail="查无此人")
    return {
        "message": "删除成功",
        "id": student_id
    }
