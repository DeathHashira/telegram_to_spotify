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

def code_verifier(num):
    possibility = string.ascii_letters + string.digits
    code = ''.join(random.choice(possibility) for _ in range(num))

    return code

def code_challenge():
    code = code_verifier(64)
    hashed = sha256(code.encode('utf-8')).digest()
    encoded = base64.urlsafe_b64encode(hashed).rstrip(b'=')

    return encoded.decode('utf-8'), code

def request_user_athurization(code_cha):
    query = {
        'client_id':client_id,
        'response_type':'code',
        'redirect_uri':redirect_uri,
        'code_challenge_method':'S256',
        'code_challenge':code_cha,
        'scope':'playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'
    }

    url = f'{base_url}/authorize?' + urllib.parse.urlencode(query)
    webbrowser.open(url=url)

def get_code():
    server = HTTPServer(('localhost', 8888), AuthHandler)
    print("Waiting for Spotify redirect...")
    server.handle_request()
    return server.code

def get_access_token(codecha, codever):
    request_user_athurization(codecha)
    auth_code = get_code()

    body = {
        'grant_type':'authorization_code',
        'code':auth_code,
        'redirect_uri':redirect_uri,
        'client_id':client_id,
        'code_verifier':codever
    }

    header = {
        'Content-Type':'application/x-www-form-urlencoded'
    }

    url = base_url + '/api/token'
    res = requests.post(url=url, data=body, headers=header)

    return res.json().get('access_token')

my_challenge, my_verified = code_challenge()
print(get_access_token(my_challenge, my_verified))

