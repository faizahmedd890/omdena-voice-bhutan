import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_chat(session_id, role, message):
    try:
        supabase.table("chats").insert({
            "session_id": session_id,
            "role": role,
            "message": message
        }).execute()
    except Exception as e:
        print("❌ save_chat error:", e)


def load_chat_history(session_id):
    try:
        response = (
            supabase
            .table("chats")
            .select("*")
            .eq("session_id", session_id)
            .order("id")
            .execute()
        )
        data = response.data
        if not data:
            return []
        return [{"role": row.get("role"), "message": row.get("message")} for row in data]
    except Exception as e:
        print("❌ load_chat_history error:", e)
        return []


def load_all_chats():
    try:
        response = (
            supabase
            .table("chats")
            .select("*")
            .order("id")
            .execute()
        )
        data = response.data
        if not data:
            return []
        return data
    except Exception as e:
        print("❌ load_all_chats error:", e)
        return []


def load_all_sessions():
    try:
        response = (
            supabase
            .table("chats")
            .select("session_id")
            .execute()
        )
        data = response.data
        if not data:
            return []
        seen = []
        for row in data:
            sid = row["session_id"]
            if sid not in seen:
                seen.append(sid)
        return seen
    except Exception as e:
        print("❌ load_all_sessions error:", e)
        return []


def delete_session(chat_id):
    try:
        supabase.table("chats").delete().eq("session_id", chat_id).execute()
    except Exception as e:
        print("❌ delete_session error:", e)


if __name__ == "__main__":
    print("✅ Supabase chat database connected successfully.")