import gpt_api_calls, mongo_manager, hackathon_reservation_selenium

# print(gpt_api_calls.get_restaurant_intention("Book me a table at Local Union 271"))
# print(
#     gpt_api_calls.get_restaurant_intention(
#         "Give me some good italian restaurants in palo alto"
#     )
# )
# print(gpt_api_calls.get_restaurant_intention("I want a house cleaner"))

# After knowing user is trying to book a restaurant, ADD a needed_info? in DB and in this entity, it will save needed_info
needed_info = {
    "restaurant_name": "",
    "party_size": "",
    "date": "",
    "time": ""
}


chat_id = mongo_manager.create_chat_document()
while any(value == "" for value in needed_info.values()):
    user_input = input("Please enter user message (type 'exit' to quit): ")
    mongo_manager.add_user_message_to_chat(chat_id, user_input)
    chat_history = mongo_manager.generate_chat_history(chat_id)
    if user_input.lower() == "exit":
        print("Exiting the loop. Goodbye!")
        break
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
        print(f"Updated needed_info: {needed_info}")

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
            
            print(f"Please provide the {missing_fields_str}.")
    ask_for_missing_info(needed_info)

print(hackathon_reservation_selenium.reserve_a_table(needed_info=needed_info))
        # if not needed_info["restaurant_name"]:
        #     print("Donna: ask user for restaurant_name(template)")
        # else:
        #     if not needed_info["party_size"]:
        #         print("Donna: ask user for party size(template)")
        #     if not needed_info["date"]:
        #         print("Donna: ask user for date(template)")
        #     if not needed_info["time"]:
        #         print("Donna: ask user for time(template)")
