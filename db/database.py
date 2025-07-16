import sqlite3

def open_connection():
    conn = sqlite3.connect('spotify.db')
    cursor = conn.cursor()

    return conn, cursor

def close_connection(conn:sqlite3.Connection):
    conn.close()

def add_new_user(conn:sqlite3.Connection, cursor:sqlite3.Cursor, email, password):
    cursor.execute('INSERT INTO users (email, passw) VALUES (?, ?)', (email, password))
    conn.commit()

def add_tokens(conn:sqlite3.Connection, cursor:sqlite3.Cursor, access_token, refresh_token, email):
    cursor.execute('UPDATE users SET access_token = ?, refresh_token = ? WHERE email = ?', (access_token, refresh_token, email))
    conn.commit()

def add_user_id(conn:sqlite3.Connection, cursor:sqlite3.Cursor, email, user_id):
    cursor.execute('UPDATE users SET user_id = ? WHERE email = ?', (user_id, email))
    conn.commit()

def add_playlist(conn:sqlite3.Connection, cursor:sqlite3.Cursor, user_id, playlist_id, playlist_name):
    cursor.execute('INSERT INTO playlists (user_id, playlist_id, playlist_name) VALUES (?, ?, ?)', (user_id, playlist_id, playlist_name))
    conn.commit()

def is_user_id(cursor:sqlite3.Cursor, email):
    cursor.execute('''
        SELECT CASE
                WHEN user_id IS NULL OR user_id = '' THEN 1
                ELSE 0
            END AS is_empty
        FROM users
        WHERE email = ?
    ''', (email,))
    
    result = cursor.fetchone()

    return result[0] if result else None

def playlists(cursor:sqlite3.Cursor, email):
    cursor.execute('''
        SELECT playlists.playlist_name
        FROM users
        JOIN playlists ON playlists.user_id = users.user_id
        WHERE users.email = ?
    ''', (email,))

    return cursor.fetchall()

def is_pass_correct(cursor:sqlite3.Cursor, email, passw):
    cursor.execute('''
        SELECT CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM users
                    WHERE email = ? AND passw = ?
                ) THEN 1
                ELSE 0
            END
    ''', (email, passw))

    return cursor.fetchone()[0]

def is_user_there(cursor:sqlite3.Cursor, email):
    cursor.execute('''
        SELECT CASE
                WHEN EXISTS (
                    SELECT 1 FROM users WHERE email = ?
                ) THEN 1
                ELSE 0
            END
    ''', (email,))

    return cursor.fetchone()[0]

def get_tokens(cursor:sqlite3.Cursor, email):
    cursor.execute('''
        SELECT access_token, refresh_token FROM users WHERE email = ?
    ''', (email,))

    result = cursor.fetchone()
    return result[0], result[1]

def update_playlist(conn:sqlite3.Connection, cursor:sqlite3.Cursor, user_id, *args):
    cursor.execute('DELETE FROM playlists WHERE user_id = ?', (user_id,))

    for item in args:
        cursor.execute('INSERT INTO playlists (user_id, playlist_id, playlist_name) VALUES (?, ?, ?)', (user_id, item[1], item[0]))

    conn.commit()

def show_user_id(cursor:sqlite3.Cursor, email):
    cursor.execute('''
        SELECT user_id FROM users WHERE email = ?
    ''', (email,))

    return cursor.fetchone()[0]