from app.config import *
import requests, urllib.parse, webbrowser, base64, random, string
from http.server import HTTPServer, BaseHTTPRequestHandler
from hashlib import sha256
from db.database import *

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        code = params.get('code')
        if code:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Authorization successful. You can close this tab.')
            self.server.code = code[0]
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Missing authorization code.')

    def log_message(self, format, *args):
        pass

class UserAccessToken:
    def __init__(self):
        self.verified_code = None
        self.challenged_code = None
        self.refresh_token = None
        self.access_token = None
    
    def __code_verifier(self, num):
        possibility = string.ascii_letters + string.digits
        self.verified_code = ''.join(random.choice(possibility) for _ in range(num))
    
    def __code_challenge(self):
        self.__code_verifier(64)
        hashed = sha256(self.verified_code.encode('utf-8')).digest()
        encoded = base64.urlsafe_b64encode(hashed).rstrip(b'=')
        self.challenged_code = encoded.decode('utf-8')
    
    def __request_user_athurization(self):
        query = {
            'client_id':client_id,
            'response_type':'code',
            'redirect_uri':redirect_uri,
            'code_challenge_method':'S256',
            'code_challenge':self.challenged_code,
            'scope':'playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-read-private user-read-email'
        }

        url = f'{base_url}/authorize?' + urllib.parse.urlencode(query)
        webbrowser.open(url=url)

    def __get_code(self):
        server = HTTPServer(('localhost', 8888), AuthHandler)
        server.handle_request()
        return server.code

    def get_access_token(self, email):
        self.__code_challenge()
        self.__request_user_athurization()
        auth_code = self.__get_code()

        body = {
            'grant_type':'authorization_code',
            'code':auth_code,
            'redirect_uri':redirect_uri,
            'client_id':client_id,
            'code_verifier':self.verified_code
        }

        header = {
            'Content-Type':'application/x-www-form-urlencoded'
        }

        url = base_url + '/api/token'
        res = requests.post(url=url, data=body, headers=header)
        self.refresh_token = res.json().get('refresh_token')
        self.access_token = res.json().get('access_token')
        conn, cursor = open_connection()
        add_tokens(conn=conn, cursor=cursor, access_token=self.access_token, 
                    refresh_token=self.refresh_token, email=email)
        close_connection(conn=conn)

    
    def refresh_access_token(self, email):
        conn, cursor = open_connection()
        cursor.execute('SELECT refresh_token from users WHERE email = ?', (email,))
        url = base_url + '/api/token'
        body = {
            'grant_type':'refresh_token',
            'refresh_token':cursor.fetchone()[0],
            'client_id':client_id
        }

        header = {
            'Content-Type':'application/x-www-form-urlencoded'
        }

        res = requests.post(url=url, data=body, headers=header)
        self.access_token = res.json().get('access_token')
        self.access_token = res.json().get('access_token')
        add_tokens(conn=conn, cursor=cursor, access_token=self.access_token, 
                    refresh_token=self.refresh_token, email=email)
        close_connection(conn=conn)

class PlayList:
    def __init__(self, plname, access_token, ispublic, iscollabrative, user_id):
        self.plname = plname
        self.header = {
            'Authorization':f'Bearer {access_token}'
        }
        self.ispublic = ispublic
        self.iscollabrative = iscollabrative
        self.playlist_id = None
        self.user_id = user_id

    def __create_playlist(self):
        url = api_url + f'/users/{self.user_id}/playlists'
        body = {
            'name':self.plname,
            'public':self.ispublic,
            'collaborative':self.iscollabrative
        }
        my_header = self.header.copy()
        my_header['Content-Type'] = 'application/json'

        res = requests.post(url=url, json=body, headers=my_header)
        self.playlist_id = res.json().get('id')
        if self.playlist_id:
            conn, cursor = open_connection()
            add_playlist(conn=conn, cursor=cursor, user_id=self.user_id, playlist_id=self.playlist_id, playlist_name=self.plname)
            close_connection(conn=conn)
        else:
            pass

    
    def find_uri(self, song_name, artist_name):
        query = f'track:{song_name} artist:{artist_name}'
        url = api_url + '/search'

        params = {
            'q':query,
            'type':'track',
            'limit':1
        }

        res = requests.get(url=url, params=params, headers=self.header)
        if res.status_code == 200:
            tracks = res.json().get('tracks', {}).get('items', [])
            if not tracks:
                return None
            
            return tracks[0]['uri']
        else:
            return None

    def add_songs(self, uris):
        if not self.playlist_id:
            self.__create_playlist()
        url = api_url + f'/playlists/{self.playlist_id}/tracks'
        body = {
            'uris':uris
        }
        my_header = self.header.copy()
        my_header['Content-Type'] = 'application/json'

        res = requests.post(url=url, json=body, headers=my_header)
    
def get_user_id(email, access_token):
        url = api_url + '/me'
        header = {
            'Authorization':f'Bearer {access_token}'
        }

        res = requests.get(url=url, headers=header)
        user_id = res.json().get('id')
        conn, cursor = open_connection()
        add_user_id(conn=conn, cursor=cursor, email=email, user_id=user_id)
        close_connection(conn=conn)

        return user_id

def list_user_playlists(user_id, access_token):
        url = api_url + f'/users/{user_id}/playlists'
        header = {
            'Authorization':f'Bearer {access_token}'
        }
        res = requests.get(url=url, headers=header)

        playlists = []
        for item in res.json()['items']:
            playlists.append((item['name'], item['id']))

        return playlists
