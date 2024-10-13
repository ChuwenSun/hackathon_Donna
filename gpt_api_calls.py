import datetime
import json
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
client = OpenAI()


def generate_prompt_based_on_chat_historyuser_chat_history(user_chat_history):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"You are an agent, and your job is to understand the latest query of the user and frame the question to be asked to the AI powered search engine, Perplexity. The user is conversing with Donna, a personal assistant. You will be fed with the chat history between the user and Donna for context. After understanding what the user's query and in the context of the past conversations between the user and Donna, frame the question that needs to be asked to Perplexity. If the user's query is asking for recommendations for sellers, service providers or places, you must ask Perplexity for google map star ratings of those sellers, service providers, or places in the question you frame for Perplexity.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_chat_history,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    return response.choices[0].message.content


def generate_sms_body(perplexity_response):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"You are an agent, and I will give you a search result which may be in a list or paragraph format. Your job is to shorten the text, remove lengthy descriptions from the text, remove contact information and ensure it can be easily read over SMS and remove the asterisk (*) and hashtag (#) from this text. If the text includes a list, use a numbered list format, keep the titles of each item and star ratings, and remove lengthy descriptions for each item.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": perplexity_response,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    return response.choices[0].message.content


def generate_place_json(perplexity_response):
    json_format = """{
    'places':
    [
    {
        "name": "string",
        "address": "string",
        "rating": "number",
        "distance": {
        "walking": "string",
        "car": "string",
        "public_transit": "string"
        },
        "phone": "string",
        "open_hours": {
        "day": "string",
        "hours": "string"
        }
    },
    {
        "name": "string",
        "address": "string",
        "rating": "number",
        "distance": {
        "walking": "string",
        "car": "string",
        "public_transit": "string"
        },
        "phone": "string",
        "open_hours": {
        "day": "string",
        "hours": "string"
        }
    },
    {
        "name": "string",
        "address": "string",
        "rating": "number",
        "distance": {
        "walking": "string",
        "car": "string",
        "public_transit": "string"
        },
        "phone": "string",
        "open_hours": {
        "day": "string",
        "hours": "string"
        }
    }
    ]
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"You are an agent, and I will give you a search result of places/locations which may be in a list or paragraph format. Your job is parse those information into a json response. Please provide the details of up to three places in the following regulated JSON format. Each place should have the fields as specified. If any information (e.g., walking, car, or public transit times) is not available, use 'No available info' as the value. Here is the required format for multiple places: {json_format} ;Please make sure to return the JSON data for all the places, even if fewer than three places are available.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": perplexity_response,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    return response_json


def generate_sms_body_by_json(json):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"Please format the following list of places into a user-friendly SMS message. Each place should include the name, rating, distance (walking or driving), Google Maps link, phone number, and open hours. Use the following format:\n\n1. [Place Name], [Rating] stars, [Distance (either walking or driving)] from you, here is the link for direction: [Google Maps link], phone: [Phone Number], opens [Open Hours]\n\n",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": str(json),
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    return response.choices[0].message.content


def generate_place_address_json(perplexity_response):
    json_format = """{
    'places':
    [
    {
        "name": "string",
        "address": "string"
    },    {
        "name": "string",
        "address": "string"
    },    {
        "name": "string",
        "address": "string"
    },
    ]
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"You are an agent, and I will give you a search result of places/locations which may be in a list or paragraph format. Your job is parse the name and street address information of those places into a json response. Here is the required format for multiple places: {json_format} ;Please make sure to return the JSON data for all the places.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": perplexity_response,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    return response_json


def update_rating(sms_body, ratings):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"You are an agent, and I will give you a sms body that I am ready to send to user and a list of place-ratings pairs. This sms includes information of place/places that user requested, but the ratings and rating counts of those places might be outdated. If there are any contents about ratings no matter from which website, delete those and update it with the real-time google map rating and rating counts which is in the provided list of place-ratings pairs from google map. Also, delete sentences like 'Check Google Maps for the latest ratings'.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"sms_body: {str(sms_body)};\nlist of place-ratings pairs from google map: {str(ratings)}",
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    return response.choices[0].message.content


def get_party_size(input):
    json_format = """{
    "party_size": "number"
    }
    """
    empty_json = """{
    "party_size": "unknown"
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"I am trying to fullfill user's request to make a reservation in a restaurant and I will give you the request sent by user. Your job is parse the party size for the reservation.Your response should be in json, Please be noted, there is possiblity that user did not include a party size info in this request, if you did not find a party size info, please respond with this: {empty_json}. If you found a party size info, here is the required format for your output: {json_format}",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    if response_json["party_size"] == "unknown":
        return ""
    return response_json["party_size"]


def get_reservation_time(input):
    json_format = """{
    "reservation_time": "string"
    }
    """
    empty_json = """{
    "reservation_time": "unknown"
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"I am trying to fullfill user's request to make a reservation in a restaurant and I will give you the request sent by user. Your job is parse the time wanted by the user for the reservation. The reservation_time value should be in 24 hr format, a example is '19:00'; The reservation_time value should be rounded to the nearest 30-minute interval, resulting in a value ending in either :00 or :30. It is possible that a user may not provide an exact time but a time frame. For example, \nExample 1: I want a table in restaurant Cotogna for dinner this friday evening.\nIn Example 1, the reservation_time can be '19:00'.\nExample 2: Can you help me make a reservation in restaurant Boulevard for lunch tomorrow around midday?\nIn Example 2, the reservation_time can be '12:00' Your response should be in json, Please be noted, there is possiblity that user did not include a reservation time info in this request, if you did not find a reservation time info, please respond with this: {empty_json}. If you found a reservation time info, here is the required format for your output: {json_format}",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    if response_json["reservation_time"] == "unknown":
        return ""
    return response_json["reservation_time"]


def get_date(input):
    json_format = """{
    "reservation_date": "string",
    "year": "string"
    }
    """
    empty_json = """{
    "reservation_date": "unknown",
    "year": "unknown"
    }
    """
    # Get the current date and time
    current_date = datetime.datetime.now()

    # Option 1: Get the day of the week as a string (e.g., "Monday")
    day_of_week_str = current_date.strftime("%A")
    # print(day_of_week_str)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"I am trying to fullfill user's request to make a reservation in a restaurant and I will give you the request sent by user. Your job is parse the date wanted by the user for the reservation. For your reference, current date is {current_date} and today is a {day_of_week_str}. Please format the date as Day, Month Abbreviation Day. The Day should be the full name of the weekday (e.g., Monday, Tuesday). The Month Abbreviation should be the first three letters of the month name (e.g., Jan, Feb, Mar), and the Day should be the numeric day of the month without a leading zero. For example, the date should look like this: Monday, Sep 30. Please be noted, there is possiblity that user did not include a date in this request, if you did not find a date, please respond with this: {empty_json}. If there is a date info found, your json response should follow this format: {json_format}",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    if (
        response_json["reservation_date"] == "unknown"
        and response_json["year"] == "unknown"
    ):
        return ""
    return response_json


def get_restaurant_name(input):
    json_format = """{
    "restaurant_name": "string"
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"I am trying to fullfill user's request to make a reservation in a restaurant and I will give you the request sent by user. Your job is parse the restaurant_name wanted by the user for the reservation. Your response should be in json, here is the required format for your output: {json_format}",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    return response_json["restaurant_name"]

def get_restaurant_intention(input):
    recommandation_json_format = """{
    "intentions": {"asking for recommandation": true, "restaurant reservation": false, "others": false}
    }
    """
    reservation_json_format = """{
    "intentions": {"asking for recommandation": false, "restaurant reservation": true, "others": false}
    }
    """
    others_json_format = """{
    "intentions": {"asking for recommandation": false, "restaurant reservation": false, "others": true}
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"I am trying to fullfill user's request for restaurant recommandation or restaurant reservation. I will feed you the message sent by the user. If user is asking for restaurant recommandation, your json response should be in this format: {recommandation_json_format}\n; If user is asking for restaurant reservation, your json response should be in this format: {reservation_json_format}\n; If user is asking neither of these 2, your json response should be in this format: {others_json_format}",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    return response_json

def get_latest_restaurant_name(input):
    json_format = """{
    "restaurant_name": "string"
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"Your job is to go through the entire chat history with the user and understand the most recent selection the user has made for a restaurant reservation and return the name of that restaurant.\nFor example:\nExample 1: ‘Please book a reservation for two people at Credo on Pine Street in San Francisco. Schedule the reservation for today at 6:15pm’\nIn Example 1, the name of the restaurant is Credo, Pine Street, San Francisco. It may be possible that the user has mentioned several restaurants in the chat history, you have to identify the most recent restaurant mentioned by the user and return that restaurant name. \n\nYour response should be in json, here is the required format for your output: {json_format}",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    return response_json["restaurant_name"]

def get_latest_date(input):
    json_format = """{
    "reservation_date": "string",
    "year": "string"
    }
    """
    empty_json = """{
    "reservation_date": "unknown",
    "year": "unknown"
    }
    """
    # Get the current date and time
    current_date = datetime.datetime.now()

    # Option 1: Get the day of the week as a string (e.g., "Monday")
    day_of_week_str = current_date.strftime("%A")
    # print(day_of_week_str)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"Your job is to go through the entire chat history with the user and find the most recent mention of a date made by the user for a restaurant reservation. \nFor your reference, current date is {current_date} and today is a {day_of_week_str}. Please format the date as Day, Month Abbreviation, Date. The Day should be the full name of the weekday (e.g., Monday, Tuesday). The Month Abbreviation should be the first three letters of the month name (e.g., Jan, Feb, Mar), and the Date should be the numeric date of the month without a leading zero. For example, the date should look like this: Monday, Sep 30. If the user has not mentioned a date in the chat, please respond with this: {empty_json}. If there is a date found, your json response should follow this format: {json_format}",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    if (
        response_json["reservation_date"] == "unknown"
        and response_json["year"] == "unknown"
    ):
        return ""
    return response_json


def get_latest_party_size(input):
    json_format = """{
    "party_size": "number"
    }
    """
    empty_json = """{
    "party_size": "unknown"
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"I am trying to handle a user's request to make a reservation in a restaurant. Your job is to go through the entire chat history with the user and find the most recent mention of the party size wanted by the user for a restaurant reservation. Your response should be in json. If the user has not mentioned a party size in their latest request, please respond with this: {empty_json}. If you found a party size info, here is the required format for your output: {json_format}",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    if response_json["party_size"] == "unknown":
        return ""
    return response_json["party_size"]

def get_latest_reservation_time(input):
    json_format = """{
    "reservation_time": "string"
    }
    """
    empty_json = """{
    "reservation_time": "unknown"
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"I am trying to handle a user's request to make a reservation in a restaurant. Your job is to go through the entire chat history with the user and find the most recent mention of a time made by the user for a restaurant reservation. The reservation_time value should be rounded to the nearest 30-minute interval, resulting in a value ending in either :00 or :30.\nIt is possible that a user may not provide an exact time but a time frame. For example, \nExample 1: I want a table in restaurant Cotogna for dinner this friday evening.\nIn Example 1, the reservation_time can be '19:00'.\nExample 2: Can you help me make a reservation in restaurant Boulevard for lunch tomorrow around midday?\nIn Example 2, the reservation_time can be '12:00' The reservation_time value should be in 24 hr format, an example is '19:00'; Your response should be in json. If the user has not mentioned a reservation time in their latest request, please respond with this: {empty_json}. If you found a reservation time info, here is the required format for your output: {json_format}",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    if response_json["reservation_time"] == "unknown":
        return ""
    return response_json["reservation_time"]

def get_selected_time_slot(input):
    json_format = """{
    "selected_timeslot": "string"
    }
    """
    empty_format = """{
    "selected_timeslot": "unknown"
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"I am an assistant and I am finishing a restaurant reservation for a user. I gave the user a list of available time slots to choose from, and the user replied to me. I will give you my message and the user's reply. Your job is to extract the time slot the user selected in the response in a 12-hour clock format with AM or PM, using no leading zero for the hour (e.g., '6:00 PM' or '9:00 AM'). Your response will be in JSON in this format: {json_format}. If the user did not select one of the options provided, this should be your response: {empty_format}"
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    if response_json["selected_timeslot"] == "unknown":
        return ""
    return response_json["selected_timeslot"]

def get_selected_seating_and_time_slot(input):
    json_format = """{
    "seating_section": "string",
    "selected_timeslot": "string"
    }
    """
    empty_format = """{
    "seating_section": "",
    "selected_timeslot": ""
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"I am an assistant and I am finishing a restaurant reservation for a user. I gave the user a list of seating sections and under each seating sections there are available time slots to choose from, and the user replied to me. I will give you my message and the user's reply. Your job is to extract the seating section and time slot the user selected in the response. The time slot should be in a 12-hour clock format with AM or PM, using no leading zero for the hour (e.g., '6:00 PM' or '9:00 AM'). Your response will be in JSON in this format: {json_format}. If you cannot identify which one user selected, this should be your response: {empty_format}"
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    # Assuming you already have the 'response' object from the API
    response_content = response.choices[0].message.content

    # Write the content into a JSON file
    # with open("response_content.json", "w") as f:
    #     json.dump(response_content, f, indent=4)

    # Then, proceed with loading it into a Python dictionary
    response_json = json.loads(response_content)
    return response_json

def generate_perplxity_prompt_based_on_message(message):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"Your job is to understand the query of the user and frame the question to be asked to the AI powered search engine, Perplexity. The user is conversing with Donna, a personal assistant. You will be fed with the conversation between the user and Donna for context. After understanding what the user's query, frame the question that needs to be asked to Perplexity. The user's query will ask for recommendations for restaurants in SF. You must ask Perplexity for 5 to 7 restaurant recommendations in accordance with the criteria provided by the user. Along with the question that you frame include the following text that will be asked to Perplexity: “Provide restaurants that take reservations online. Don't suggest the most popular restaurants as they are hard to find reservations for. Restaurants that have between 4 and 4.4 star ratings should be fine",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    return response.choices[0].message.content

def generate_simplified_restaurant_list_sms(input):
    example_restaurant_list = "1. name of restaurant A\n2. name of restaurant B\n3. name of restaurant C"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"I am trying to send user a list of restaurant names as a response to a request of recommandation. Now I will feed you a response generated by perplxity which will includes a list of restaurants with some detailed information and unrelated language. Your job is to extract the restaurant names in that list. And simply give me a numbered list of restaurant name with nothing else. Here is a example of your response: {example_restaurant_list}",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input,
                    }
                ],
            },
        ],
        temperature=0.1,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
    )
    # logger.info(f"text response from zipcode chat completion: {response.choices[0].message.content}")
    # it is just responding a json format str

    return response.choices[0].message.content