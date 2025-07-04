from config import *
import requests, urllib.parse, webbrowser, base64
from http.server import HTTPServer, BaseHTTPRequestHandler

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        code = params.get('code')
        if code:
            print("Authorization code received:", code[0])
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Authorization successful. You can close this tab.')
            self.server.code = code[0]
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Missing authorization code.')

def request_user_athurization():
    query = {
        'client_id':client_id,
        'response_type':'code',
        'redirect_uri':redirect_uri
    }

    url = f'{base_url}/authorize?' + urllib.parse.urlencode(query)
    webbrowser.open(url=url)

def get_code():
    server = HTTPServer(('localhost', 8888), AuthHandler)
    print("Waiting for Spotify redirect...")
    server.handle_request()
    return server.code

def get_access_token():
    request_user_athurization()
    auth_code = get_code()

    body = {
        'grant_type':'authorization_code',
        'code':auth_code,
        'redirect_uri':redirect_uri
    }

    header = {
        'Authorization':f'Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}',
        'Content-Type':'application/x-www-form-urlencoded'
    }

    url = base_url + '/api/token'
    res = requests.post(url=url, data=body, headers=header)

    return res.json().get('access_token')

print(get_access_token())

