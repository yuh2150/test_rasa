import requests
import json

class BookingAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def create_booking(self, quote_id, passenger_info):

        url = f"{self.base_url}"
        payload = {
            "quoteId": quote_id,
            "passenger": passenger_info
        }

        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(payload))

            if response.status_code == 200:
                return response.json()  # Successful response
            else:
                return {
                    "error": response.status_code,
                    "message": response.text
                }
        except requests.exceptions.RequestException as e:
            return {"error": "Request failed", "message": str(e)}

if __name__ == "__main__":
    api = BookingAPI(
        base_url="https://dispatch.local.goodjourney.io/api/demand/v1/bookings",
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmbGVldElkIjoieWVsbG93IiwidGhpcmRQYXJ0eSI6IlZpbmNlbnQgQVBJIiwiYXBwTmFtZSI6IlZpbmNlbnQgQVBJIiwiX2lkIjoiNjU5NzgwMjQ1YTNmMmI0YzAyOGU1ZjlkIiwiaWF0IjoxNzI2NDUxNzMwLCJleHAiOjE3MjY0NTUzMzAsImF1ZCI6ImF1dGguZ29qby5nbG9iYWwifQ.l49LIBE5twMvebBUXkKkgU3lnCMk4KvEG_qTupwFZ3c"  # Replace with your token
    )
    passenger_info = {
        "title": "Mr",
        "phone": "09184854845",
        "firstName": "Huy",
        "lastName": ""
    }

    # Create booking request
    response = api.create_booking(
        quote_id="5bc3ffff-e684-4263-bc90-b86be5addcf8",
        passenger_info=passenger_info
    )

    print(response.get('status'))