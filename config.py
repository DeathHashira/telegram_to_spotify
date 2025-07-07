from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

redirect_uri = 'http://127.0.0.1:8888/callback'
base_url = 'https://accounts.spotify.com'
api_url = 'https://api.spotify.com/v1'