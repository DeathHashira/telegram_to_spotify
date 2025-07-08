import sqlite3

conn = sqlite3.connect('spotify.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    passw TEXT NOT NULL,
    user_id TEXT,
    access_token TEXT,
    refresh_token TEXT
)
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlists (
    user_id TEXT NOT NULL,
    playlist_id TEXT NOT NULL,
    playlist_name TEXT NOT NULL
)
''')

conn.commit()
conn.close()