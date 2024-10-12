import csv
import requests
from dotenv import load_dotenv
from openai import OpenAI
import os
import logging

# Configure logging to write to a file named 'places_api.log'
logging.basicConfig(
    filename="places_api.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

load_dotenv()
api_key = os.environ.get("GOOGLE_MAPS_API_KEY")


def get_restaurant_ratings_v1(places):
    """
    Get Google Maps star ratings for a list of restaurants using the new v1 Places API and log API responses.

    Args:
        places (list of dict): List of dictionaries, each containing 'name' and optionally 'address'.
                               Example: [{'name': 'Restaurant A', 'address': '123 Main St, City'},
                                         {'name': 'Restaurant B'}]
        api_key (str): Your Google Places API key.

    Returns:
        dict: Dictionary with restaurant names as keys and their star ratings and user ratings as values.
              Example: {'Restaurant A': {'rating': 4.5, 'userRatingCount': 120}, 'Restaurant B': {'rating': 3.8, 'userRatingCount': 85}}
    """
    base_url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        # Updated FieldMask to include user ratings total along with other fields
        "X-Goog-FieldMask": "places.displayName,places.rating,places.userRatingCount",
    }
    ratings = {}

    for place in places:
        # Construct the query using name and address
        query = place["name"]
        if "address" in place:
            query_with_address = f"{place['name']} {place['address']}"
        else:
            query_with_address = place["name"]

        # Function to make the API request
        def make_request(query):
            payload = {"textQuery": query}
            response = requests.post(base_url, headers=headers, json=payload)
            data = response.json()
            logging.info(f"Request for: {query}")
            logging.info(f"Response: {data}")
            return data

        # Make the initial request with name + address
        data = make_request(query_with_address)

        # Check if the response is empty or contains no valid place data
        if not data.get("places") or len(data["places"]) == 0:
            logging.warning(
                f"No data found for {query_with_address}, retrying with name only..."
            )
            # Retry with just the restaurant name
            data = make_request(place["name"])

        # Process the response data
        if "error" in data:
            logging.error(
                f"Error for {query}: {data['error'].get('message', 'No error message provided')}"
            )
            ratings[place["name"]] = {
                "rating": "Error",
                "userRatingCount": "No rating available",
            }
            continue

        # Extract rating and user ratings total from the best matched place
        if "places" in data and len(data["places"]) > 0:
            best_match = data["places"][0]
            ratings[place["name"]] = {
                "rating": best_match.get("rating", "No rating available"),
                "userRatingCount": best_match.get(
                    "userRatingCount", "No user ratings available"
                ),
            }
        else:
            ratings[place["name"]] = {
                "rating": "No rating available",
                "userRatingCount": "No user ratings available",
            }

    return ratings


def get_restaurant_details_and_export_to_csv(
    places, output_file="MV_GM_api_info_reservable.csv"
):
    """
    Retrieve detailed information for a list of restaurants using the Google Places API and export the results to a CSV file.

    Args:
        places (list of dict): List of dictionaries, each containing 'name' and optionally 'address'.
                               Example: [{'name': 'Restaurant A', 'address': '123 Main St, City'},
                                         {'name': 'Restaurant B'}]
        api_key (str): Your Google Places API key.
        output_file (str): The name of the CSV file where the results will be saved.

    Returns:
        None
    """
    base_url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "places.displayName,places.id,places.rating,places.userRatingCount,places.currentOpeningHours,"
            "places.currentSecondaryOpeningHours,places.internationalPhoneNumber,places.nationalPhoneNumber,"
            "places.priceLevel,places.regularOpeningHours,places.regularSecondaryOpeningHours,places.websiteUri,"
            "places.addressComponents,places.adrFormatAddress,places.businessStatus,places.formattedAddress,"
            "places.googleMapsUri,places.iconBackgroundColor,places.iconMaskBaseUri,places.location,"
            "places.photos,places.plusCode,places.primaryType,places.types,places.utcOffsetMinutes,places.viewport"
        ),
    }

    # Initialize an empty list to hold all restaurant data for CSV export
    all_restaurants_data = []

    # Define the header for the CSV file based on the fields specified
    csv_header = [
        "Name",
        "Place ID",
        "Rating",
        "User Rating Count",
        "Current Opening Hours",
        "Current Secondary Opening Hours",
        "International Phone Number",
        "National Phone Number",
        "Price Level",
        "Regular Opening Hours",
        "Regular Secondary Opening Hours",
        "Website URI",
        "Address Components",
        "ADR Format Address",
        "Business Status",
        "Formatted Address",
        "Google Maps URI",
        "Icon Background Color",
        "Icon Mask Base URI",
        "Location",
        "Photos",
        "Plus Code",
        "Primary Type",
        "Types",
        "UTC Offset Minutes",
        "Viewport",
    ]

    for place in places:
        # Construct the query using name and address
        query = place["name"]
        if "address" in place:
            query += f" {place['address']}"

        # Prepare payload for API request
        payload = {"textQuery": query}
        response = requests.post(base_url, headers=headers, json=payload)
        data = response.json()

        logging.info(f"Request for: {query}")
        logging.info(f"Response: {data}")

        # Extract the first matching place's details if available
        if "places" in data and len(data["places"]) > 0:
            place_details = data["places"][0]
            # Create a dictionary to hold the place's information, using the fields in csv_header
            place_data = {
                "Name": place_details.get("displayName", "No name available"),
                "Place ID": place_details.get("id", "No ID available"),
                "Rating": place_details.get("rating", "No rating available"),
                "User Rating Count": place_details.get(
                    "userRatingCount", "No user ratings available"
                ),
                "Current Opening Hours": place_details.get(
                    "currentOpeningHours", "No current opening hours available"
                ),
                "Current Secondary Opening Hours": place_details.get(
                    "currentSecondaryOpeningHours",
                    "No secondary opening hours available",
                ),
                "International Phone Number": place_details.get(
                    "internationalPhoneNumber",
                    "No international phone number available",
                ),
                "National Phone Number": place_details.get(
                    "nationalPhoneNumber", "No national phone number available"
                ),
                "Price Level": place_details.get(
                    "priceLevel", "No price level available"
                ),
                "Regular Opening Hours": place_details.get(
                    "regularOpeningHours", "No regular opening hours available"
                ),
                "Regular Secondary Opening Hours": place_details.get(
                    "regularSecondaryOpeningHours",
                    "No secondary regular hours available",
                ),
                "Website URI": place_details.get("websiteUri", "No website available"),
                "Address Components": place_details.get(
                    "addressComponents", "No address components available"
                ),
                "ADR Format Address": place_details.get(
                    "adrFormatAddress", "No ADR format address available"
                ),
                "Business Status": place_details.get(
                    "businessStatus", "No business status available"
                ),
                "Formatted Address": place_details.get(
                    "formattedAddress", "No formatted address available"
                ),
                "Google Maps URI": place_details.get(
                    "googleMapsUri", "No Google Maps URI available"
                ),
                "Icon Background Color": place_details.get(
                    "iconBackgroundColor", "No icon background color available"
                ),
                "Icon Mask Base URI": place_details.get(
                    "iconMaskBaseUri", "No icon mask base URI available"
                ),
                "Location": place_details.get("location", "No location available"),
                "Photos": place_details.get("photos", "No photos available"),
                "Plus Code": place_details.get("plusCode", "No plus code available"),
                "Primary Type": place_details.get(
                    "primaryType", "No primary type available"
                ),
                "Types": place_details.get("types", "No types available"),
                "UTC Offset Minutes": place_details.get(
                    "utcOffsetMinutes", "No UTC offset minutes available"
                ),
                "Viewport": place_details.get("viewport", "No viewport available"),
            }
            # Append the place's data to the list
            all_restaurants_data.append(place_data)
        else:
            logging.warning(f"No data found for {query}.")
            # If no data is found, create an empty record with default values
            place_data = {header: "No data available" for header in csv_header}
            place_data["Name"] = place["name"]
            all_restaurants_data.append(place_data)

    # Write all collected restaurant data to the CSV file
    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_header)
        writer.writeheader()
        writer.writerows(all_restaurants_data)

    logging.info(f"Data exported to {output_file} successfully.")


# example usage:

# places_list = [
#     {"name": "Kin Khao", "address": "55 Cyril Magnin St, San Francisco, CA 94102"},
#     {"name": "Burma Superstar", "address": "3095 Fillmore St, San Francisco, CA 94123"},
#     {"name": "Mr. Jiu's", "address": "28 Waverly Pl, San Francisco, CA 94108"},
#     {
#         "name": "Farmhouse Kitchen Thai Cuisine",
#         "address": "710 Florida St, San Francisco, CA 94110",
#     },
#     {"name": "San Tung", "address": "1031 Irving St, San Francisco, CA 94122"},
# ]

# print(get_restaurant_ratings_v1(places_list))
