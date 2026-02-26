from sqlite3 import IntegrityError
from typing import Optional
import datetime
from fastapi import Depends, FastAPI, HTTPException, Request
from auth import create_token, get_current_user, pwd_context

from pydantic import BaseModel

from database import get_connection, init_db

app = FastAPI()
init_db()


class Note(BaseModel):
    title: str
    content: str


class User(BaseModel):
    email: str
    password: str
    username: str
    fullname: str


class UserInfo(BaseModel):
    email: Optional[str] = None
    password: str
    username: Optional[str] = None


@app.get("/notes")
def get_notes(user_id: int = Depends(get_current_user)):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE user_id = ?", (user_id,))
        notes_list = cursor.fetchall()
        return [dict(note) for note in notes_list]


@app.post("/note")
def post_notes(note: Note, user_id: int = Depends(get_current_user)):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (title, content, created_at, user_id) VALUES (?, ?, ?, ?)",
            (note.title, note.content, datetime.datetime.now().isoformat(), user_id,)
        )
        conn.commit()
        note_id = cursor.lastrowid

        return {
            "id": note_id,
            "title": note.title,
            "content": note.content
        }


@app.get("/note/{note_id}")
def get_note(note_id: int, user_id: int = Depends(get_current_user)):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM notes WHERE id = ? AND user_id = ?",
            (note_id, user_id,)
        )
        note = cursor.fetchone()

        if note is None:
            raise HTTPException(status_code=404, detail="NOTE NOT FOUND")
        return {"note": dict(note)}


@app.put("/note/{note_id}")
def update_note(note_id: int, note: Note, user_id: int = Depends(get_current_user)):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE notes SET title = ?, content = ? WHERE id = ? AND user_id = ?",
            (note.title, note.content, note_id,)
        )

        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="NOTE NOT FOUND")

        return {"message": "Note updated successfully"}


@app.delete("/note/{note_id}")
def delete_note(note_id: int, user_id: int = Depends(get_current_user)):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM notes WHERE id= ? AND user_id = ?",
            (note_id, user_id,)
        )

        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="NOTE NOT FOUND")

        return {"message": "Note Deleted successfully"}


@app.get("/users")
def get_users(user_id: int = Depends(get_current_user)):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, username, fullname FROM users")
        user_list = cursor.fetchall()
        return {"user": [dict(u) for u in user_list]}


@app.delete("/user/{user_id}")
def delete_user(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM users WHERE id= ?",
            (user_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="USER NOT FOUND")

        return {"message": "User Deleted successfully"}


@app.post("/signup")
def user_signup(user: User):

    # Hash a password
    hashed = pwd_context.hash(user.password)

    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (email, password, username, fullname) VALUES (?, ?, ?, ?)",
                (user.email, hashed, user.username, user.fullname,)
            )
            conn.commit()
            user_id = cursor.lastrowid

            return {
                "id": user_id,
                "email": user.email,
                "username": user.username,
                "fullname": user.fullname
            }
        except IntegrityError:
            raise HTTPException(
                status_code=409, detail="Email already registered")


@app.post("/login")
def user_login(user_info: UserInfo):
    with get_connection() as conn:

        cursor = conn.cursor()

        if user_info.username:
            cursor.execute("SELECT * FROM users WHERE username = ?",
                           (user_info.username,))
        elif user_info.email:
            cursor.execute("SELECT * FROM users WHERE email = ?",
                           (user_info.email,))
        else:
            raise HTTPException(
                status_code=400, detail="Provide username or email")

        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user = dict(row)

        # Verify a password
        flag = pwd_context.verify(user_info.password, user["password"])

        if (flag):
            token = create_token(int(user["id"]))

            return {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "fullname": user["fullname"],
                "token": token
            }
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
