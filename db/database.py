import sqlite3

def open_connection():
    conn = sqlite3.connect('spotify.db')
    cursor = conn.cursor()

    return conn, cursor

def close_connection(conn:sqlite3.Connection):
    conn.close()

def add_new_user(conn:sqlite3.Connection ,cursor:sqlite3.Cursor, email, password):
    cursor.execute('INSERT INTO users (name, passw) VALUES (?, ?)', (email, password))
    conn.commit()

def add_tokens(conn:sqlite3.Connection ,cursor:sqlite3.Cursor, access_token, refresh_token, email):
    cursor.execute('UPDATE users SET access_token = ?, refresh_tokne = ? WHERE email = ?', (access_token, refresh_token, email))
    conn.commit()

def add_user_id(conn:sqlite3.Connection ,cursor:sqlite3.Cursor, email, user_id):
    cursor.execute('UPDATE users SET user_id = ? WHERE email = ?', (user_id, email))
    conn.commit()

def add_playlist(conn:sqlite3.Connection ,cursor:sqlite3.Cursor, user_id, playlist_id, playlist_name):
    cursor.execute('INSERT INTO playlists (user_id, playlist_id, playlist_name) VALUES (?, ?, ?)', (user_id, playlist_id, playlist_name))
    conn.commit()