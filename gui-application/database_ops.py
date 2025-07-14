import sqlite3

DB_PATH = "ai-tutor-data.db"

def get_connection_to_db():
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_database_tables (conn):

    cursor = conn.cursor()

    # Enable foreign key constraint support
    cursor.execute("PRAGMA foreign_keys = ON")

    # Create 'chapters' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chapter_name TEXT NOT NULL,
        confidence_score REAL DEFAULT 0.0
    )
    ''')

    # Create 'sections' table with foreign key to 'chapters'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chapter_id INTEGER NOT NULL,
        section_id INTEGER NOT NULL,
        section_text TEXT,
        quiz_score REAL DEFAULT 0.0,
        FOREIGN KEY(chapter_id) REFERENCES chapters(id)
    )
    ''')
    conn.commit()

def insert_chapter(conn, chapter_name, confidence_score):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chapters (chapter_name, confidence_score)
        VALUES (?, ?)
    ''', (chapter_name, confidence_score))
    conn.commit()
    return cursor.lastrowid

def insert_section(conn, chapter_id, section_id, section_text, quiz_score):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sections (chapter_id, section_id, section_text, quiz_score)
        VALUES (?, ?, ?, ?)
    ''', (chapter_id, section_id, section_text, quiz_score))
    conn.commit()

def get_all_chapters(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chapters")
    results = cursor.fetchall()
    return results

def get_sections_by_chapter(conn, chapter_id):
    # given a chapter id, get corresponding sections
    cursor = conn.cursor()
    cursor.execute('''
        SELECT section_id, section_text, quiz_score
        FROM sections
        WHERE chapter_id = ?
    ''', (chapter_id,))
    results = cursor.fetchall()
    return results

def close_connection(conn):
    conn.close()