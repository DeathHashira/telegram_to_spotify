
# Telefy – Telegram to Spotify Playlist Converter

**Telefy** is a lightweight desktop application that converts a Telegram chat export (`.json`) into a Spotify playlist. Built with **PyQt6** for the GUI and **SQLite3** for local storage, this tool helps you relive shared music memories by turning Telegram music mentions into actual playlists on Spotify.

---

## 🎯 Purpose

The goal of this app is simple:  
**Extract music mentions from Telegram chats and build a Spotify playlist with those tracks.**

---

## 🧠 How It Works

1. **You export a Telegram chat** (in JSON format).
2. **You load that JSON into the app** via the GUI.
3. The app:
   - Parses the chat to find potential music entries (usually from links, messages, or patterns).
   - Queries the **Spotify Web API** to find matches.
   - Saves search results to a local **SQLite3 database**.
   - Creates a new **Spotify playlist** and adds all matched songs to it.

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/DeathHashira/telegram_to_spotify.git
cd telegram_to_spotify
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Main dependencies:**

- `PyQt6` – GUI framework
- `spotipy` – Spotify API wrapper
- `python-dotenv` – Load credentials from `.env`
- `sqlite3` – Built-in database (no installation needed)

> You can also install manually:
> ```bash
> pip install PyQt6 spotipy python-dotenv
> ```

### 3. Create a Spotify App

Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and create a new application.

Note the following:
- **Client ID**
- **Client Secret**
- Add a redirect URI (e.g. `http://localhost:8888/callback`)

### 4. Set Up `.env` File

In the root of the project, create a file named `.env` and fill it like this:

```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

---

## ▶️ How to Run the App

From the root of the project:

```bash
python -m app.main
```

This will launch the PyQt6 GUI, where you can load your Telegram chat JSON file and convert it to a Spotify playlist.

---

## 💾 Local Database

This project uses **SQLite3**, a lightweight serverless database, to:

- Store matched song–track data
- Cache results to avoid redundant API calls
- Persist progress across app runs

The database is created and managed locally on your system (e.g., `telefy.db`), and doesn't require any setup or online server.

---

## 🧪 Current Release: Telefy v1.008 Beta

This is the **first beta release** of Telefy. Here's what to know:

- The app **should function correctly** if all configurations are set properly.
- However, **there is no bug handling yet**. If something goes wrong (bad file, API error, etc.), the app might **crash** without warning.
- If **everything works but no results appear**, it's likely due to a **403 Forbidden response** from Spotify. This is usually related to:
  - Expired token
  - Bad internet connection
  - API rate limiting
- For now, error feedback is limited. Always check your `.env` file and internet connection if you're stuck.

---

## 📌 Notes

- The app is designed for personal use and small-scale conversions.
- More robust error handling, fuzzy matching, and batch search improvements are planned in future versions.
- Contributions and ideas are welcome!

---

## 📄 License

[MIT License](LICENSE)

---

## 👤 Author

**[DeathHashira](https://github.com/DeathHashira)**  
Telegram to Spotify made simple.
