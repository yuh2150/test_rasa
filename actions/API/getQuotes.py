import requests
import json

# from geoCoding import GeoCodingAPI
# import pytz
# from datetime import datetime, timedelta

class QuotesAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

    def get_quotes(self, pickup_datetime, pickup_coords, destination_coords):
        payload = json.dumps({
            "pickupDateTime": pickup_datetime,
            "pickup": {
                "latitude": pickup_coords['latitude'],
                "longitude": pickup_coords['longitude'],
            },
            "destination": {
                "latitude": destination_coords['latitude'],
                "longitude": destination_coords['longitude'],
            },
        })

        try:
            response = requests.post(self.base_url, headers=self.headers, data=payload)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error: {response.status_code}, {response.text}"}
        except requests.RequestException as e:
            return {"error": str(e)}
class Quote:
    def __init__(self, quote_id, expires_at, vehicle_type, price_value, price_currency, luggage, passengers, provider_name, provider_phone):
        self.quote_id = quote_id
        self.expires_at = expires_at
        self.vehicle_type = vehicle_type
        self.price_value = price_value
        self.price_currency = price_currency
        self.luggage = luggage
        self.passengers = passengers
        self.provider_name = provider_name
        self.provider_phone = provider_phone

    def __repr__(self):
        return (f"Quote(quote_id={self.quote_id}, expires_at={self.expires_at}, vehicle_type={self.vehicle_type}, "
                f"price_value={self.price_value}, price_currency={self.price_currency}, luggage={self.luggage}, "
                f"passengers={self.passengers}, provider_name={self.provider_name}, provider_phone={self.provider_phone})")
# # Example usage
# if __name__ == "__main__":
#     token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmbGVldElkIjoieWVsbG93IiwidGhpcmRQYXJ0eSI6IlZpbmNlbnQgQVBJIiwiYXBwTmFtZSI6IlZpbmNlbnQgQVBJIiwiX2lkIjoiNjU5NzgwMjQ1YTNmMmI0YzAyOGU1ZjlkIiwiaWF0IjoxNzI2NDU4MTg2LCJleHAiOjE3MjY0NjE3ODYsImF1ZCI6ImF1dGguZ29qby5nbG9iYWwifQ.8ahaXoPK6ahLn0xI-rH36txWCiluwJLMxGmX8B_atcM"
    
#     geoCodingAPI = GeoCodingAPI("https://map.local.goodjourney.io/api/mapProvider/geoCoding")    
#     quotesAPI = QuotesAPI("https://dispatch.local.goodjourney.io/api/demand/v1/quotes",token=token)
    
#     geoCoding_pickup = geoCodingAPI.get_geocoding("271 Nguyen Van Linh" + ", Da Nang" )
#     geoCoding_destination = geoCodingAPI.get_geocoding("470 Tran Dai Nghia" + ", Da Nang")
#     now_utc = datetime.now(pytz.utc)

#     # Format the time in ISO 8601 format
#     current_time_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

#     # Parse the current ISO 8601 time string back to a datetime object with UTC timezone
#     current_time_dt = datetime.strptime(current_time_iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)

#     # Add 7 hours (GMT+7)
#     new_dt = current_time_dt + timedelta(hours=7)

#     # Format the new datetime object back to ISO 8601 format
#     pickup_datetime = new_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

#     # pickup_coords = { "latitude": 16.059052,"longitude": 108.2112656,}
#     # destination_coords = { "latitude": 16.0595717,"longitude": 108.2111016,}
#     pickup_coords = { "latitude": float(geoCoding_pickup['results'][0]['geometry']['location']['lat']),"longitude": float(geoCoding_pickup['results'][0]['geometry']['location']['lng']),}
#     destination_coords = { "latitude": float(geoCoding_destination['results'][0]['geometry']['location']['lat']),"longitude": float(geoCoding_destination['results'][0]['geometry']['location']['lng']),}
    
    
#     quotes_data = quotesAPI.get_quotes(pickup_datetime, pickup_coords, destination_coords)
    
    # print (quotes_data)
