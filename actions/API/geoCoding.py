import requests

import requests

class GeoCodingAPI:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_geocoding(self, address, channel="chatbot"):
        params = {
            "address": address,
            "channel": channel
        }
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error: {response.status_code}"}
        except requests.RequestException as e:
            return {"error": str(e)}
