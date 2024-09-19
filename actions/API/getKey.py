import json
import requests
from requests.auth import HTTPBasicAuth

class OAuthClient:
    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None

    def get_token(self):
        # payload = json.dumps({})
        try:
            response = requests.get(
                self.base_url,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                data=json.dumps({}),
                auth=HTTPBasicAuth(self.client_id, self.client_secret)
            )

            if response.status_code == 200:
                self.token = response.json().get("access_token")
                return self.token
            else:
                return f"Error: {response.status_code}, {response.text}"
        except requests.RequestException as e:
            return f"Request failed: {str(e)}"


if __name__ == "__main__":

    oauth_client = OAuthClient(
        base_url="https://dispatch.local.goodjourney.io/api/demand/oauth/token",
        client_id="ck-0a003ed2bf354cdcf73b5f98edab77f2",
        client_secret="sk-47279af8d764362a25e00c87e5127f67dcf39e5aa8952f4eb4c4d9ac518bf904"
    )
    token = oauth_client.get_token()
    
    print(token)
