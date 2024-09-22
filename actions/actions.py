
import logging
import json
import pytz

from typing import Any, Dict, List, Text, Optional
from datetime import datetime, timedelta
from rasa_sdk import Action, Tracker
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
)

from actions.API.booking import BookingAPI
from actions.API.geoCoding import GeoCodingAPI
from actions.API.getKey import OAuthClient
from actions.API.getQuotes import QuotesAPI


# quotes = []
token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmbGVldElkIjoieWVsbG93IiwidGhpcmRQYXJ0eSI6IlZpbmNlbnQgQVBJIiwiYXBwTmFtZSI6IlZpbmNlbnQgQVBJIiwiX2lkIjoiNjU5NzgwMjQ1YTNmMmI0YzAyOGU1ZjlkIiwiaWF0IjoxNzI2NzQwNDU3LCJleHAiOjE3MjY3NDQwNTcsImF1ZCI6ImF1dGguZ29qby5nbG9iYWwifQ.byzmxPxqbtNmYUphaPArnKp_3NF7EG4yjAswdE2_ukE"

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
    def to_dict(self):
        return {
            "quote_id": self.quote_id,
            "expires_at": self.expires_at,
            "vehicle_type": self.vehicle_type,
            "price_value": self.price_value,
            "price_currency": self.price_currency,
            "luggage": self.luggage,
            "passengers": self.passengers,
            "provider_name": self.provider_name,
            "provider_phone": self.provider_phone
        }
    def __repr__(self):
        return (f"Quote(quote_id={self.quote_id}, expires_at={self.expires_at}, vehicle_type={self.vehicle_type}, "
                f"price_value={self.price_value}, price_currency={self.price_currency}, luggage={self.luggage}, "
                f"passengers={self.passengers}, provider_name={self.provider_name}, provider_phone={self.provider_phone})")

class ActionCurrentTime(Action):
    def name(self) -> Text:
        return "action_current_time"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the current time in UTC.
        now_utc = datetime.now(pytz.utc)
        
        # Format the time in ISO 8601 format
        current_time_iso = now_utc.isoformat(timespec='milliseconds')
        
        # Send the formatted time to the user
        dispatcher.utter_message(text=f"The current time is {current_time_iso}")
        
        return []

class ActionGreetUser(Action):
    """Greets the user with/without privacy policy"""

    def name(self) -> Text:
        return "action_greet_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get the current time in UTC.
        
        intent = tracker.latest_message["intent"].get("name")
        shown_privacy = tracker.get_slot("shown_privacy")
        name_entity = next(tracker.get_latest_entity_values("name"), None)
        if intent == "greet" or (intent == "enter_data" and name_entity):
            if shown_privacy and name_entity and name_entity.lower() != "sara":
                dispatcher.utter_message(response="utter_greet_name", name=name_entity)
                return []
            elif shown_privacy:
                dispatcher.utter_message(response="utter_greet_noname")
                return []
            else:
                dispatcher.utter_message(response="utter_greet")
                # dispatcher.utter_message(response="utter_inform_privacypolicy")
                return [SlotSet("shown_privacy", True)]
        return []
class ActionGeoCoding(Action):
    def name(self) -> Text:
        return "action_geocoding"
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> List[EventType]:
        
        pick_up_location = tracker.get_slot("pick_up_location")
        destination_location = tracker.get_slot("destination_location")
        
        geoCodingAPI = GeoCodingAPI("https://map.local.goodjourney.io/api/mapProvider/geoCoding")
        
        geoCoding_pickup = geoCodingAPI.get_geocoding(pick_up_location )
        geoCoding_destination = geoCodingAPI.get_geocoding(destination_location )
        
         # List to store slot updates
        slot_updates = []
        
        # Check pickup location geocoding result
        if geoCoding_pickup["status"] == "OK":
            # Assuming the geocoding response has a formatted address or coordinates
            slot_updates.append(SlotSet("pick_up_location", geoCoding_pickup))  # Store only the address or relevant info
        else:
            dispatcher.utter_message(response="utter_invalid_pick_up_location")
            slot_updates.append(SlotSet("requested_slot", "pick_up_location"))
        
        # Check destination location geocoding result
        if geoCoding_destination["status"] == "OK":
            # Assuming the geocoding response has a formatted address or coordinates
            slot_updates.append(SlotSet("destination_location", geoCoding_destination))  # Store only the address or relevant info
        else:
            dispatcher.utter_message(response="utter_invalid_destination_location")
            slot_updates.append(SlotSet("requested_slot", "destination_location"))
        
        return slot_updates
class ActionaAskConfirmInfo(Actiona):
    def name(self) -> Text:
        return "action_ask_confirm_info"
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> List[EventType]:
        
        pick_up_time = tracker.get_slot("pick_up_time")
        pick_up_location = tracker.get_slot("pick_up_location")
        destination_location = tracker.get_slot("destination_location")
        person_name = tracker.get_slot("person_name")
        number_contact = tracker.get_slot("number_contact")
        
        dispatcher.utter_message(text=f"Please confirm your ride details:\n"
                              f"- Pickup Location: {pick_up_location['results'][0]['formatted_address']}\n"
                              f"- Destination: {destination_location['results'][0]['formatted_address']}\n"
                              f"- Pickup Time: {pick_up_time}\n"
                              f"- Name: {person_name}\n"
                              f"- Contact Number: {number_contact}\n")
        return []
        
class ActionSubmitBookFormToGetQuotes(Action):
    def name(self) -> Text:
        return "action_submit_book_ride_form_to_get_quotes"
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[EventType]:

        pick_up_time = tracker.get_slot("pick_up_time")
        pick_up_location = tracker.get_slot("pick_up_location")
        destination_location = tracker.get_slot("destination_location")
        person_name = tracker.get_slot("person_name")
        number_contact = tracker.get_slot("number_contact")
        # date = datetime.datetime.now().strftime("%d/%m/%Y")

        # book_info = [person_name, number_contact,pick_up_location,destination_location,pick_up_time]
        
        # geoCodingAPI = GeoCodingAPI("https://map.local.goodjourney.io/api/mapProvider/geoCoding")    
        quotesAPI = QuotesAPI("https://dispatch.local.goodjourney.io/api/demand/v1/quotes",token=token)
        
        # geoCoding_pickup = geoCodingAPI.get_geocoding(pick_up_location + ", Da Nang" )
        # geoCoding_destination = geoCodingAPI.get_geocoding(destination_location + ", Da Nang")
        now_utc = datetime.now(pytz.utc)

        # Format the time in ISO 8601 format
        current_time_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Parse the current ISO 8601 time string back to a datetime object with UTC timezone
        current_time_dt = datetime.strptime(current_time_iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)

        # Add 7 hours (GMT+7)
        new_dt = current_time_dt + timedelta(hours=7)

        # Format the new datetime object back to ISO 8601 format
        pickup_datetime = new_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # pickup_coords = { "latitude": 16.059052,"longitude": 108.2112656,}
        # destination_coords = { "latitude": 16.0595717,"longitude": 108.2111016,}
        pickup_coords = { "latitude": float(geoCoding_pickup['results'][0]['geometry']['location']['lat']),"longitude": float(geoCoding_pickup['results'][0]['geometry']['location']['lng']),}
        destination_coords = { "latitude": float(geoCoding_destination['results'][0]['geometry']['location']['lat']),"longitude": float(geoCoding_destination['results'][0]['geometry']['location']['lng']),}
        
        
        quotes_data = quotesAPI.get_quotes(pickup_datetime, pickup_coords, destination_coords)

        return [SlotSet("quotes", quotes_data)]
    
class ActionDisplaySelectQuotes(Action):
    def name(self) -> Text:
        return "action_display_select_quotes"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        buttons = []
        quotes_data = tracker.get_slot("quotes")
        quotes = []
        for item in quotes_data:
            quote = Quote(
            quote_id=item['quoteId'],
            expires_at=item['expiresAt'],
            vehicle_type=item['vehicleType'],
            price_value=item['price']['value'],
            price_currency=item['price']['currency'],
            luggage=item['luggage'],
            passengers=item['passengers'],
            provider_name=item['provider']['name'],
            provider_phone=item['provider']['phone']
            )
            quotes.append(quote)

        for quote in quotes:
            buttons.append({
                "title": f"{quote.vehicle_type} - {quote.price_value} {quote.price_currency}",
                "payload": f"/choose_quote{{\"quoteId\": \"{quote.quote_id}\"}}"
            })
        dispatcher.utter_message(buttons = buttons)
        return []
    
class ActionPerformBookingRide(Action):
    def name(self) -> Text:
        return "action_perform_booking_ride"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,) -> List[EventType]:
        
        bookingAPI = BookingAPI("https://dispatch.local.goodjourney.io/api/demand/v1/bookings",token=token)
        quote_id = tracker.get_slot("quoteId")
        person_name = tracker.get_slot("person_name")
        number_contact = tracker.get_slot("number_contact")
        
        passenger_info = {
            "title": "Mr",
            "phone": number_contact,
            "firstName": person_name,
            "lastName": ""
        }

        # Create booking request
        response = bookingAPI.create_booking(
            quote_id=quote_id,
            passenger_info=passenger_info
        )
        
        dispatcher.utter_message(response.get('status'))
        # dispatcher.utter_message(text=response)
        return []

