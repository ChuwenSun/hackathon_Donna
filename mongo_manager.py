import json
import pandas as pd
from pymongo import MongoClient
import datetime
import pytz
from logger_config import setup_logger
import os
from dotenv import load_dotenv

logger = setup_logger(__name__)
# MongoDB setup
# MongoDB Atlas connection string (use environment variables for security)
load_dotenv()
MONGO_URI = os.getenv("MONGO_CONNECTION_STR")
# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)
# client = MongoClient('localhost', 27017)
db = client["sms_service_db"]
users_collection = db["users"]
tokens_collection = db["tokens"]
system_collection = db["system"]
chat_queue_collection = db["chat_queue"]
payment_links_collection = db["payment_links"]
jobs_collection = db["schedule_messages"]
restaurants_MV_collection = db["restaurants_MV"]
restaurants_collection = db["restaurants"]
hackathon_chat_history_collection = db["hackathon_chat_history"]

def store_user_sms_message(user_phone, message_body, photo_url=None, user_name=None):
    """
    Stores an SMS message in the user's chat history in MongoDB.

    :param user_phone: The phone number of the user (as a string).
    :param message_body: The message body (as a string).
    :return: None
    """

    # Define San Francisco timezone (Pacific Time)
    sf_timezone = pytz.timezone("America/Los_Angeles")
    chat = {
        "role": "User",
        "message": message_body,
        "timestamp": datetime.datetime.now(sf_timezone).isoformat(),
        "photo_url": photo_url,
    }

    # Update user's chat history and user name in MongoDB
    users_collection.update_one(
        {"user_phone": user_phone},  # Filter by user_phone
        {
            "$push": {"chat_history": chat},  # Push the chat to chat_history
            "$set": {"user_name": user_name},  # Set or update the user_name
        },
        upsert=True,  # Create a new document if no match is found
    )


def store_Donna_sms_message(user_phone, message_body, photo_url=None):
    """
    Stores an SMS message in the user's chat history in MongoDB.

    :param user_phone: The phone number of the user (as a string).
    :param message_body: The message body (as a string).
    :return: None
    """

    # Define San Francisco timezone (Pacific Time)
    sf_timezone = pytz.timezone("America/Los_Angeles")
    chat = {
        "role": "Donna",
        "message": message_body,
        "timestamp": datetime.datetime.now(sf_timezone).isoformat(),
        "photo_url": photo_url,
    }

    # Update user's chat history in MongoDB
    users_collection.update_one(
        {"user_phone": user_phone}, {"$push": {"chat_history": chat}}, upsert=True
    )


def save_tokens(token_json):
    """
    Save OAuth tokens in MongoDB's tokens_collection.
    :param token_json: The token data to be saved (as JSON).
    """
    try:
        tokens_collection.update_one(
            {"_id": "google_calendar"},  # Single document to store tokens
            {"$set": {"tokens": json.dumps(token_json)}},  # Save as JSON string
            upsert=True,
        )
        logger.info("Tokens saved.")
    except Exception as e:
        logger.error(f"Error saving tokens: {e}")
        raise


def save_tokens_for_calendar(token_json):
    """
    Save OAuth tokens in MongoDB's tokens_collection.
    :param token_json: The token data to be saved (as JSON).
    """
    try:
        tokens_collection.update_one(
            {"_id": "google_calendar"},  # Single document to store tokens
            {"$set": {"tokens": json.dumps(token_json)}},  # Save as JSON string
            upsert=True,
        )
        logger.info("Tokens saved.")
    except Exception as e:
        logger.error(f"Error saving tokens: {e}")
        raise


def load_tokens():
    """
    Load OAuth tokens from MongoDB's tokens_collection and convert them to a dictionary.
    :return: The tokens as a dictionary if they exist, or None if not found.
    """
    try:
        token_data = tokens_collection.find_one({"_id": "google_calendar"})
        if token_data and "tokens" in token_data:
            logger.info("Tokens loaded.")
            return json.loads(
                token_data["tokens"]
            )  # Convert the token string back to a dictionary
        else:
            logger.info("No tokens found.")
            return None
    except Exception as e:
        logger.error(f"Error loading tokens: {e}")
        raise


def load_tokens_for_calendar():
    """
    Load OAuth tokens from MongoDB's tokens_collection and convert them to a dictionary.
    :return: The tokens as a dictionary if they exist, or None if not found.
    """
    try:
        token_data = tokens_collection.find_one({"_id": "google_calendar"})
        if token_data and "tokens" in token_data:
            logger.info("Tokens loaded.")
            return json.loads(
                token_data["tokens"]
            )  # Convert the token string back to a dictionary
        else:
            logger.info("No tokens found.")
            return None
    except Exception as e:
        logger.error(f"Error loading tokens: {e}")
        raise


def get_one_user_chat_history(user_phone):
    return users_collection.find_one(
        {"user_phone": user_phone}, {"_id": 0, "chat_history": 1}
    )


def store_a_payment_link(user_phone, payment_link, user_name):
    payment_link_object = {
        "_id": payment_link,  # Use payment_link as the unique identifier
        "user": user_phone,
        "user_name": user_name,
        "created_at": datetime.datetime.now(),
    }
    try:
        payment_links_collection.insert_one(payment_link_object)
    except Exception as e:
        print(f"An error occurred: {e}")


def get_user_by_payment_link(payment_link):
    result = payment_links_collection.find_one(
        {"_id": payment_link}, {"_id": 0, "user": 1, "user_name": 1}
    )
    if result:
        return result  # Return the document containing both user and user_name
    else:
        return None  # Return None if no matching document is found


def start_a_task_for_a_user(user_phone, task_name):

    # Define San Francisco timezone (Pacific Time)
    sf_timezone = pytz.timezone("America/Los_Angeles")
    task = {
        "task_name": task_name,
        "start_time": datetime.datetime.now(sf_timezone).isoformat(),
        "status": "Active",
    }

    # Update user's chat history in MongoDB
    users_collection.update_one(
        {"user_phone": user_phone}, {"$push": {"tasks": task}}, upsert=True
    )


def finish_a_task_for_a_user(user_phone, task_name):

    # Define San Francisco timezone (Pacific Time)
    sf_timezone = pytz.timezone("America/Los_Angeles")
    end_time = datetime.datetime.now(sf_timezone).isoformat()

    # Update the task's status to 'Finished' and add the end time
    users_collection.update_one(
        {
            "user_phone": user_phone,
            "tasks.task_name": task_name,
            "tasks.status": "Active",
        },
        {"$set": {"tasks.$.status": "Finished", "tasks.$.end_time": end_time}},
    )


def abort_a_task_for_a_user(user_phone, task_name):

    # Define San Francisco timezone (Pacific Time)
    sf_timezone = pytz.timezone("America/Los_Angeles")
    end_time = datetime.datetime.now(sf_timezone).isoformat()

    # Update the task's status to 'Aborted' and add the end time
    users_collection.update_one(
        {
            "user_phone": user_phone,
            "tasks.task_name": task_name,
            "tasks.status": "Active",
        },
        {"$set": {"tasks.$.status": "Aborted", "tasks.$.end_time": end_time}},
    )


def get_all_tasks_of_a_user(user_phone):
    # Find the user by phone number and return the tasks
    user = users_collection.find_one(
        {"user_phone": user_phone},
        {"_id": 0, "tasks": 1},  # Exclude the _id field, include only the tasks field
    )

    # Return the tasks if the user exists, otherwise return an empty list
    if user and "tasks" in user:
        return user["tasks"]
    else:
        return []


def get_user_name_by_phone(user_phone):
    user_data = users_collection.find_one(
        {"user_phone": user_phone}, {"_id": 0, "user_name": 1}
    )
    if user_data and "user_name" in user_data:
        return user_data["user_name"]
    return None  # Return None if no user_name is found or user doesn't exist


def update_system_status(status):
    try:
        system_collection.update_one(
            {"_id": "system_status"},  # Single document to store tokens
            {"$set": {"system_status": str(status)}},  # Save as JSON string
            upsert=True,
        )
        logger.info(f"system_status updated to {status}.")
    except Exception as e:
        logger.error(f"Error saving system_status: {e}")
        raise


def get_system_status():
    system_record = system_collection.find_one({"_id": "system_status"})
    if system_record and "system_status" in system_record:
        return system_record["system_status"]
    return None  # Return None if no system_status is found or user doesn't exist


def store_Donna_sms_message_in_queue(
    user_phone, message_body, photo_url=None, payment_link=None
):
    """
    Stores an SMS message in queue to send next time system online.

    :param user_phone: The phone number of the user (as a string).
    :param message_body: The message body (as a string).
    :return: None
    """

    # Define San Francisco timezone (Pacific Time)
    sf_timezone = pytz.timezone("America/Los_Angeles")
    chat = {
        "role": "Donna",
        "message": message_body,
        "timestamp": datetime.datetime.now(sf_timezone).isoformat(),
        "photo_url": photo_url,
        "payment_link": payment_link,
    }

    # Update user's chat history in MongoDB
    chat_queue_collection.update_one(
        {"user_phone": user_phone}, {"$push": {"chat_history": chat}}, upsert=True
    )


def get_chat_queue_collection():

    # Fetch all documents in the collection
    chat_queue_data = chat_queue_collection.find()

    # Convert cursor to list and return it
    return list(chat_queue_data)


def clear_chat_queue_collection():
    result = chat_queue_collection.delete_many({})

    # Return the number of documents deleted
    return result.deleted_count


def get_phone_latest_message_dict():

    # Dictionary to store the latest message for each user
    latest_chat_objects = {}

    # Query the collection
    cursor = users_collection.find(
        {}, {"user_phone": 1, "chat_history": 1}
    )  # Fetches only user_phone and chat_history fields
    for document in cursor:
        user_phone = document["user_phone"]
        chat_history = document["chat_history"]
        if chat_history:  # Ensure there is at least one message in chat history
            latest_chat = chat_history[-1]  # Get the latest chat object
            latest_chat_objects[user_phone] = latest_chat  # Store the whole JSON object

    return latest_chat_objects


def get_phone_latest_message(user_phone):
    # Query the collection for a specific user using their phone number
    document = users_collection.find_one(
        {"user_phone": user_phone}, {"chat_history": 1}
    )  # Fetches only chat_history field

    if (
        document and "chat_history" in document and document["chat_history"]
    ):  # Ensure the user and chat history exist
        latest_chat = document["chat_history"][
            -1
        ]  # Get the latest chat object (last one in the list)
        return latest_chat  # Return the latest chat object

    # If the user is not found or chat_history is empty, return None or a default value
    return None


def get_user_referral(phone_number):
    # Search for the user by phone number
    user = users_collection.find_one({"user_phone": phone_number})

    # Check if the user has a 'referral' field and return its value
    if user and "referral" in user:
        return user["referral"] if user["referral"] else False
    return False


def get_users_by_name_substr(name_str):
    # Create a case-insensitive regex search for first name or last name
    name_regex = {"$regex": name_str, "$options": "i"}

    # Find all users whose user_name matches the search string
    query = {"user_name": name_regex}
    matched_users = list(users_collection.find(query))
    return matched_users
    # if len(matched_users) == 1:
    #     # Only one match, return the phone number
    #     return matched_users[0]['user_phone']
    # elif len(matched_users) > 1:
    #     # Multiple matches found
    #     return f"Multiple users found for '{name_str}'. Please be more specific."
    # else:
    #     # No matches found
    #     return f"No users found for '{name_str}'."


def save_job_to_db(job_id, message_body, phone_number, scheduled_time):
    job_data = {
        "job_id": job_id,
        "message_body": message_body,
        "phone_number": phone_number,
        "scheduled_time": scheduled_time,
        "status": "scheduled",
    }
    jobs_collection.insert_one(job_data)


def get_pendings_jobs():
    # greater than?
    return jobs_collection.find({"status": "scheduled"})


def delete_a_scheduled_message(job_id):
    jobs_collection.delete_one({"job_id": job_id})


def get_places_from_mongodb():

    collection = restaurants_MV_collection

    # Query the collection to get all documents and their 'name' fields
    documents = collection.find({}, {"name": 1})

    # Create a list of places with static address 'Mountain View'
    places = [
        {"name": doc["name"], "address": "Mountain View"}
        for doc in documents
        if "name" in doc
    ]

    return places


def import_seating_sections_MV():
    def normalize_name(name):
        return name.strip().lower()

    file_path = "MV_seating_sections.csv"
    csv_data = pd.read_csv(file_path)
    collection = restaurants_MV_collection
    # Iterate through each row in the CSV and update the corresponding document in MongoDB
    for index, row in csv_data.iterrows():
        restaurant_name = normalize_name(row["Restaurant Name"])
        seating_sections = row["seating Sections"]

        # Update the restaurant document in MongoDB
        result = collection.update_one(
            {"name": {"$regex": f"^{restaurant_name}$", "$options": "i"}},
            {"$set": {"seating_sections": eval(seating_sections)}},
        )

        # Output update status for debugging
        if result.matched_count > 0:
            print(
                f"Updated {restaurant_name} with seating sections: {seating_sections}"
            )
        else:
            print(f"No document found for {restaurant_name}")

    print("Update complete.")


def add_automatic_reserve_field(successful_restaurants):
    def normalize_name(name):
        return name.strip().lower()

    collection = restaurants_collection  # Replace with your collection name

    # Track results
    matched_count = 0
    modified_count = 0

    # Use `find_one` to check and update each restaurant individually
    for restaurant in successful_restaurants:
        # Try to find the restaurant document with an exact match on 'name'
        found_document = collection.find_one({"name": restaurant})

        if found_document:
            # If the document is found, update it with the 'automatic_reserve' field
            result = collection.update_one(
                {"_id": found_document["_id"]}, {"$set": {"automatic_reserve": True}}
            )

            # Increment counters based on the update result
            matched_count += 1
            modified_count += result.modified_count
            print(f"Updated document for restaurant: {restaurant}")
        else:
            print(f"No document found for restaurant: {restaurant}")

    print(f"Matched {matched_count} documents and modified {modified_count} documents.")


def find_TODO_restaurants():
    missing_fields_documents = restaurants_MV_collection.find(
        {
            "$nor": [
                {"automatic_reserve": {"$exists": True}},
                {"walk-in": {"$exists": True}},
                {"manual_reservation": {"$exists": True}},
            ]
        }
    )

    # Print out the results
    for doc in missing_fields_documents:
        print(doc)


def add_city_field_to_collection():
    collection = restaurants_collection

    # Update all documents in the collection by adding a 'city' field with value 'mountain view'
    result = collection.update_many({}, {"$set": {"city": "palo alto"}})

    # Print the result summary
    print(
        f"Matched {result.matched_count} documents and modified {result.modified_count} documents."
    )


def copy_collection():
    # Connect to MongoDB
    client = MongoClient(
        "mongodb://localhost:27017/"
    )  # Replace with your MongoDB URI if different

    # Define the source and destination collections
    source_collection = restaurants_MV_collection
    dest_collection = restaurants_collection

    # Fetch all documents from the source collection
    documents = list(
        source_collection.find({})
    )  # Retrieve all documents from the source collection

    if documents:
        # Insert all documents into the destination collection
        insert_result = dest_collection.insert_many(documents)
        print(
            f"Successfully copied {len(insert_result.inserted_ids)} documents from 'restaurants_MV_collection' to 'restaurants_collection'"
        )
    else:
        print(
            f"No documents found in the source collection '{restaurants_MV_collection}'."
        )


def what_is_this_restaurant(restaurant_name):  # Replace with your collection name

    # Find the document for the given restaurant name (case-insensitive match)
    restaurant = restaurants_collection.find_one(
        {"name": {"$regex": f"^{restaurant_name}$", "$options": "i"}}
    )

    # Check which field exists in the restaurant document
    if restaurant:
        if "automatic_reserve" in restaurant:
            return "automatic_reserve"
        elif "walk-in" in restaurant:
            return "walk-in"
        elif "manual_reservation" in restaurant:
            return "manual_reservation"
    else:
        return f"Restaurant '{restaurant_name}' not found in the collection."


def get_seating_sections(restaurant_name):
    collection = restaurants_collection

    # Query the collection for a document with the given restaurant name
    restaurant = collection.find_one({"name": restaurant_name})

    # Check if the document has the 'seating_sections' field and return it
    if restaurant and "seating_sections" in restaurant:
        return restaurant["seating_sections"]
    else:
        return "not_needed"

def create_chat_document():
    """
    Creates a new document for the chat history with an empty array for messages.
    """
    chat_document = {
        "chat_id": str(datetime.datetime.now()),  # You can generate chat_id differently if needed
        "messages": []  # Empty array to store chat messages
    }
    inserted_id = hackathon_chat_history_collection.insert_one(chat_document).inserted_id
    return inserted_id

def add_user_message_to_chat(chat_id, user_input):
    """
    Adds a message to the existing chat history document.
    """
    message = {
        "role": "user",
        "content": user_input,
        "timestamp": datetime.datetime.now().isoformat()
    }
    hackathon_chat_history_collection.update_one(
        {"_id": chat_id},
        {"$push": {"messages": message}}
    )
def add_assistant_message_to_chat(chat_id, assistant_input):
    """
    Adds a message to the existing chat history document.
    """
    message = {
        "role": "assistant",
        "content": assistant_input,
        "timestamp": datetime.datetime.now().isoformat()
    }
    hackathon_chat_history_collection.update_one(
        {"_id": chat_id},
        {"$push": {"messages": message}}
    )

def generate_chat_history(chat_id):
    """
    Generates the chat history of a document in a readable format.
    
    Args:
        chat_id: The ID of the chat document.
    
    Returns:
        A formatted string of the entire chat history.
    """
    # Fetch the chat document by ID
    chat_document = hackathon_chat_history_collection.find_one({"_id": chat_id})
    
    if not chat_document or "messages" not in chat_document:
        return "No chat history found for this ID."

    # Initialize an empty string to hold the formatted chat history
    chat_history = ""

    # Iterate over the messages and format them
    for message in chat_document["messages"]:
        role = message.get("role", "unknown")
        content = message.get("content", "")
        chat_history += f"{role}: {content}\n"
    
    return chat_history

def create_user_chat_document(user_phone):
    """
    Creates a new document for the chat history with an empty array for messages.
    """
    needed_info = {
        "restaurant_name": "",
        "party_size": "",
        "date": "",
        "time": ""
    }
    chat_document = {
        "user_phone": user_phone,  # You can generate chat_id differently if needed
        "messages": [],  # Empty array to store chat messages
        "needed_info": needed_info
    }
    hackathon_chat_history_collection.insert_one(chat_document)
    logger.info(f"insert new chat_document for {user_phone}")
def check_user_chat_exists(user_phone):
    """
    Checks if a document for the given user_phone already exists in the MongoDB collection.
    
    :param user_phone: Phone number of the user
    :return: True if the document exists, False otherwise
    """
    # Query MongoDB to check if the document exists
    user_chat_document = hackathon_chat_history_collection.find_one({"user_phone": user_phone})
    
    if user_chat_document:
        logger.info(f'found a chat document for {user_phone}')
        return True
    else:
        logger.info(f'Did not found a chat document for {user_phone}')
        return False
    
def add_user_message_to_chat_V2(user_phone, user_input):
    """
    Adds a message to the existing chat history document based on user_phone.
    
    :param user_phone: Phone number of the user
    :param user_input: The message content from the user
    """
    message = {
        "role": "user",
        "content": user_input,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Update the document with the matching user_phone and push the message to the 'messages' array
    hackathon_chat_history_collection.update_one(
        {"user_phone": user_phone},
        {"$push": {"messages": message}}
    )

    logger.info(f"User message added to chat for phone number: {user_phone}")
def add_assistant_message_to_chat_V2(user_phone, assistant_input):
    """
    Adds a message to the existing chat history document based on user_phone.
    
    :param user_phone: Phone number of the user
    :param user_input: The message content from the user
    """
    message = {
        "role": "assistant",
        "content": assistant_input,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Update the document with the matching user_phone and push the message to the 'messages' array
    hackathon_chat_history_collection.update_one(
        {"user_phone": user_phone},
        {"$push": {"messages": message}}
    )

    logger.info(f"Assistant message added to chat for phone number: {user_phone}")
def add_assistant_message_to_chat(chat_id, assistant_input):
    """
    Adds a message to the existing chat history document.
    """
    message = {
        "role": "assistant",
        "content": assistant_input,
        "timestamp": datetime.datetime.now().isoformat()
    }
    hackathon_chat_history_collection.update_one(
        {"_id": chat_id},
        {"$push": {"messages": message}}
    )

def get_needed_info(user_phone):
    """
    Retrieves the 'needed_info' field for a given user_phone from the MongoDB collection.
    
    :param user_phone: Phone number of the user
    :return: The 'needed_info' dictionary if found, or None if no document is found
    """
    # Query to find the document by user_phone
    user_chat_document = hackathon_chat_history_collection.find_one({"user_phone": user_phone}, {"_id": 0, "needed_info": 1})
    
    if user_chat_document and "needed_info" in user_chat_document:
        return user_chat_document["needed_info"]
    else:
        logger.info(f"No document found for phone number: {user_phone}")
        return None
    
def update_needed_info(user_phone, updated_info):
    """
    Updates the 'needed_info' field for the given user_phone in the MongoDB collection.
    
    :param user_phone: Phone number of the user
    :param updated_info: Dictionary with updated values for 'needed_info'
    :return: None
    """
    # Update the document that matches the user_phone
    result = hackathon_chat_history_collection.update_one(
        {"user_phone": user_phone},
        {"$set": {"needed_info": updated_info}}
    )
    
    if result.matched_count > 0:
        print(f"'needed_info' updated for phone number: {user_phone}")
    else:
        print(f"No document found for phone number: {user_phone}")
