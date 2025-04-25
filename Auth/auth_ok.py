import requests

def get_ok_access_token(code):
    url = "https://api.ok.ru/oauth/token.do"
    params = {
        "code": code,
        "redirect_uri": "https://oauth.yandex.ru/verification_code",
        "grant_type": "authorization_code",
        "client_id": "",
        "client_secret": ""
    }
    response = requests.post(url, data=params)
    return response.json()

session_token = ""

token = get_ok_access_token(session_token) # работает 30 минут
print("🎫 Access Token Response:", token)
