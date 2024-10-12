import re
import datetime
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
import os
from openai import OpenAI
import json
import sys
import stripe
import time
from twilio.twiml.messaging_response import MessagingResponse
from flask_apscheduler import APScheduler
import urllib
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import gpt_api_calls
import hackathon_reservation_selenium
import mongo_manager, google_map_manager
from twilio.rest import Client
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from logger_config import setup_logger
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pytz
from dateutil import parser
from app import scheduler

logger = setup_logger(__name__)

main = Blueprint("main", __name__)

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
if auth_token is None:
    logger.error("No auth token")
twilio_client = Client(account_sid, auth_token)
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

sf_timezone = pytz.timezone("America/Los_Angeles")




# Path to your service account credentials file
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
]
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]

# The range to check in the spreadsheet (adjust based on your sheet structure)
RANGE_NAME = "Sheet1!A2:F"  # Assuming "Phone" is in column D
NOTIFICATION_EMAIL_LIST = ["chuwensun2067@gmail.com", "harshitk@stanford.edu"]



# Function to normalize phone numbers (remove spaces, parentheses, and dashes)
def normalize_phone_number(phone):
    # Remove all characters that are not digits
    cleaned_phone = re.sub(r"[^\d]", "", phone)

    # Check if the phone number starts with a country code (e.g., +1)
    if not cleaned_phone.startswith("1"):
        # Prepend the country code +1 for US numbers
        cleaned_phone = "1" + cleaned_phone

    # Add the plus sign to the start of the number
    return "+" + cleaned_phone


def send_message_to_hackathon_user(user_phone, message_body):
    logger.info(
        f"Sending message manually: {message_body} to {user_phone}"
    )

    message = twilio_client.messages.create(
        body=message_body,
        from_="+18666131185",
        to=user_phone,
    )
    # redis_manager.append_to_conversation_history(phone, 'Donna', message_text)
    logger.info(
        f"Sent message manually: {message_body} to {user_phone}"
    )    

@main.route("/sms", methods=["GET", "POST"])
def get_info():
    resp = MessagingResponse()
    user_message = request.values.get("Body", None)
    photo_url = request.values.get("MediaUrl0", None)
    user_phone = request.values.get("From", None)

    
    
    if not mongo_manager.check_user_chat_exists(user_phone):
        logger.info("new user should be created")
        mongo_manager.create_user_chat_document(user_phone)

    needed_info = mongo_manager.get_needed_info(user_phone)
    logger.info(f"current needed_info is {needed_info}")
    if any(value == "" for value in needed_info.values()):
        user_input = user_message
        mongo_manager.add_user_message_to_chat_V2(user_phone, user_input)
        if user_input.lower() == "exit":
            print("Exiting the loop. Goodbye!")
            return resp
        else:        
            if not needed_info["restaurant_name"]:
                needed_info["restaurant_name"] = gpt_api_calls.get_restaurant_name(user_input)
            if not needed_info["party_size"]:
                needed_info["party_size"] = gpt_api_calls.get_party_size(user_input)
            if not needed_info["date"]:
                needed_info["date"] = gpt_api_calls.get_date(user_input)
            if not needed_info["time"]:
                needed_info["time"] = gpt_api_calls.get_reservation_time(user_input)
            # if needed_info["seating_section"] != "not_needed":
            #     print(
            #         f"\nDonna: I need you to choose one seating section from below: {needed_info['seating_section']}"
            #     )
            logger.info(f"Updated needed_info: {needed_info}")
            mongo_manager.update_needed_info(user_phone, needed_info)
        def ask_for_missing_info(needed_info):
            missing_fields = []

            if not needed_info["restaurant_name"]:
                missing_fields.append("restaurant name")
            if not needed_info["party_size"]:
                missing_fields.append("party size")
            if not needed_info["date"]:
                missing_fields.append("date")
            if not needed_info["time"]:
                missing_fields.append("time")

            if missing_fields:
                # Join the missing fields in a grammatically correct way
                missing_fields_str = ', '.join(missing_fields[:-1])
                if len(missing_fields) > 1:
                    missing_fields_str += f" and {missing_fields[-1]}"
                else:
                    missing_fields_str = missing_fields[0]
                send_message_to_hackathon_user(user_phone, f"Please provide the {missing_fields_str}.")
                # print(f"Please provide the {missing_fields_str}.")
        ask_for_missing_info(needed_info)

    if not any(value == "" for value in needed_info.values()):
        print(hackathon_reservation_selenium.reserve_a_table(needed_info=needed_info))
    return resp