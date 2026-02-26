import sqlite3
import uuid
from datetime import datetime
import chromadb
from app.config import DB_PATH, CHROMA_PATH
from app.schemas import Commitment


# ─── SQLite Setup ────────────────────────────────────────────

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates tables if they don't exist. Runs on startup."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commitments (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            meeting_title TEXT NOT NULL,
            task TEXT NOT NULL,
            owner TEXT,
            deadline TEXT,
            priority TEXT,
            is_vague INTEGER,
            status TEXT DEFAULT 'open',
            created_at TEXT NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized.")


# ─── ChromaDB Setup ──────────────────────────────────────────

def get_chroma_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name="commitments")
    return collection


# ─── Save Meeting ─────────────────────────────────────────────

def save_meeting(title: str) -> str:
    """Creates a meeting record. Returns meeting_id."""
    meeting_id = str(uuid.uuid4())
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO meetings (id, title, created_at) VALUES (?, ?, ?)",
        (meeting_id, title, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return meeting_id


# ─── Save Commitments ─────────────────────────────────────────

def save_commitments(meeting_id: str, meeting_title: str, commitments: list[Commitment]):
    """
    Saves all commitments to SQLite and ChromaDB.
    Both stores updated together — always in sync.
    """
    conn = get_db_connection()
    collection = get_chroma_collection()

    for commitment in commitments:
        commitment_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        # Save to SQLite
        conn.execute("""
            INSERT INTO commitments 
            (id, meeting_id, meeting_title, task, owner, deadline, priority, is_vague, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)
        """, (
            commitment_id,
            meeting_id,
            meeting_title,
            commitment.task,
            commitment.owner,
            commitment.deadline,
            commitment.priority,
            int(commitment.is_vague),
            created_at
        ))

        # Save to ChromaDB
        collection.add(
            ids=[commitment_id],
            documents=[commitment.task],
            metadatas=[{
                "meeting_id": meeting_id,
                "meeting_title": meeting_title,
                "owner": commitment.owner or "unassigned",
                "deadline": commitment.deadline or "none",
                "priority": commitment.priority,
                "status": "open",
                "created_at": created_at
            }]
        )

    conn.commit()
    conn.close()


# ─── Retrieve Commitments ─────────────────────────────────────

def get_all_commitments():
    """Returns all commitments from SQLite."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM commitments ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_commitments_by_owner(owner: str):
    """Returns all commitments for a specific owner."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM commitments WHERE owner = ? ORDER BY created_at DESC",
        (owner,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ─── Semantic Search ──────────────────────────────────────────

def search_similar_commitments(query: str, n_results: int = 5):
    """
    Searches ChromaDB semantically.
    This is the cross-meeting memory feature.
    Used by the /query endpoint.
    """
    collection = get_chroma_collection()
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results