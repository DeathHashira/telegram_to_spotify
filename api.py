from config import *
import requests, urllib.parse, webbrowser, base64, random, string
from http.server import HTTPServer, BaseHTTPRequestHandler
from hashlib import sha256

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
        print("Waiting for Spotify redirect...")
        server.handle_request()
        return server.code

    def get_access_token(self):
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
    
    def refresh_access_token(self):
        url = base_url + '/api/token'
        body = {
            'grant_type':'refresh_token',
            'refresh_token':self.refresh_token,
            'client_id':client_id
        }

        header = {
            'Content-Type':'application/x-www-form-urlencoded'
        }

        res = requests.post(url=url, data=body, headers=header)
        self.access_token = res.json().get('access_token')

class PlayList:
    def __init__(self, plname, access_token, ispublic, iscollabrative):
        self.plname = plname
        self.header = {
            'Authorization':f'Bearer {access_token}'
        }
        self.ispublic = ispublic
        self.iscollabrative = iscollabrative
        self.playlist_id = None
        self.user_id = None


    def __get_user_id(self):
        url = api_url + '/me'

        res = requests.get(url=url, headers=self.header)
        self.user_id = res.json().get('id')

    def __create_playlist(self):
        self.__get_user_id()
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
    
    def find_uri(self, song_name, artist_name):
        query = f'track:{song_name} artist:{artist_name}'
        url = api_url + '/search'

        params = {
            'q':query,
            'type':'track',
            'limit':1
        }

        res = requests.get(url=url, params=params, headers=self.header)
        tracks = res.json().get('tracks', {}).get('items', [])
        if not tracks:
            return None
        
        return tracks[0]['uri']

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
