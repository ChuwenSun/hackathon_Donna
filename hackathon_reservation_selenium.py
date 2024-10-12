import csv
import datetime
import json
import random
import re
import time
import urllib
import gpt_api_calls
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import gpt_api_calls
from logger_config import setup_logger
from exceptions import (
    DateUnavailableException,
    TimeUnavailableException,
    UnexpectedScriptError,
    OpenTableOptionNotFoundException,
    EmailInputNotAvailableException,
    TimeSlotsNotFoundException,
    FinalReserveBtnNotAvailableException,
)
import undetected_chromedriver as uc
import pandas as pd

logger = setup_logger(__name__)

month_mapping = {
    "Jan": "January",
    "Feb": "February",
    "Mar": "March",
    "Apr": "April",
    "May": "May",
    "Jun": "June",
    "Jul": "July",
    "Aug": "August",
    "Sep": "September",
    "Oct": "October",
    "Nov": "November",
    "Dec": "December",
}

def generate_random_sleep_time(lower, upper):
    # Generate a random float between lower and upper
    sleep_time = random.uniform(lower, upper)
    # Sleep for the generated amount of time
    time.sleep(sleep_time)
    print(f"randomly sleeping for {sleep_time} seconds")


def enter_value_fake_slowly(lower, upper, input_element, string):
    for char in string:
        input_element.send_keys(char)
        generate_random_sleep_time(lower, upper)


def initializeDriver():
    """
    this function initialize ChromeDriver with options
    to keep the browser open after script execution

    Args:
        None
    Returns:
        ChromeDriver instance
    """
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--lang=en")
    # options.add_argument("user-data-dir=C:/Users/ssccw/AppData/Local/Google/Chrome/User Data/Profile 7")
    options.add_argument(
        r"--user-data-dir=C:/Users/ssccw/AppData/Local/Google/Chrome/User Data"
    )  # e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
    options.add_argument(r"--profile-directory=Profile 7")  # e.g. Profile 3
    service = Service(
        executable_path="D:\ChromeDriver\chromedriver-win64\chromedriver.exe"
    )
    # driver = webdriver.Chrome(executable_path=r'D:\ChromeDriver\chromedriver-win64\chromedriver.exe', chrome_options=options)
    options.add_argument("--remote-debugging-pipe")
    driver = webdriver.Chrome(service=service, options=options)

    # options.add_argument(f'--proxy-server={proxy}')
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--window-size=1920,1080")

    # driver = webdriver.Chrome(options=options)
    return driver


def initializeUcDriver_with_user_profile():
    """
    This function initializes ChromeDriver with options
    to keep the browser open after script execution using `undetected-chromedriver`.

    Args:
        None
    Returns:
        ChromeDriver instance
    """
    # Initialize options for Chrome
    options = uc.ChromeOptions()
    options.add_argument("--lang=en")  # Set language to English
    # options.add_argument("--start-maximized")
    # profile = "C:\\Users\\ssccw\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 7"
    # options.add_argument(rf"user-data-dir={profile}")
    options.add_argument(
        "--user-data-dir=C:/Users/samya/AppData/Local/Google/Chrome/User Data"
    )
    # options.add_argument("--profile-directory=Profile 9")
    # options.add_argument(r"--user-data-dir=C:/Users/ssccw/AppData/Local/Google/Chrome/User Data")  # Path to Chrome User Data
    options.add_argument("--profile-directory=Profile 10")  # Use specific Chrome profile"

    # Additional arguments to avoid detection
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--remote-debugging-pipe")  # For remote debugging

    # Specify ChromeDriver path
    # service = Service(executable_path='D:/ChromeDriver/chromedriver-win64/chromedriver.exe')

    # Initialize the undetected ChromeDriver with options and service
    # driver = uc.Chrome(service=service, options=options)
    driver = uc.Chrome(options=options, use_subprocess=True)
    # Return the driver instance without detach
    return driver


def initializeUcDriver():
    """
    This function initializes ChromeDriver with options
    to keep the browser open after script execution using `undetected-chromedriver`.

    Args:
        None
    Returns:
        ChromeDriver instance
    """
    # Initialize options for Chrome
    options = uc.ChromeOptions()
    options.add_argument("--lang=en")  # Set language to English
    # options.add_argument("--start-maximized")
    # profile = "C:\\Users\\ssccw\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 7"
    # options.add_argument(rf"user-data-dir={profile}")
    # options.add_argument("--user-data-dir=C:/Users/ssccw/AppData/Local/Google/Chrome/User Data")
    # options.add_argument("--profile-directory=Profile 9")
    # options.add_argument(r"--user-data-dir=C:/Users/ssccw/AppData/Local/Google/Chrome/User Data")  # Path to Chrome User Data
    # options.add_argument("--profile-directory=Profile 7")  # Use specific Chrome profile

    # Additional arguments to avoid detection
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--remote-debugging-pipe")  # For remote debugging

    # Specify ChromeDriver path
    # service = Service(executable_path='D:/ChromeDriver/chromedriver-win64/chromedriver.exe')

    # Initialize the undetected ChromeDriver with options and service
    # driver = uc.Chrome(service=service, options=options)
    driver = uc.Chrome(options=options, use_subprocess=True)
    # Return the driver instance without detach
    return driver


def convert_24hr_to_12hr(time_str):
    # Convert the input time string into a datetime object
    time_obj = datetime.datetime.strptime(time_str, "%H:%M")
    # Convert the datetime object to a 12-hour format string with AM/PM notation
    return time_obj.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")


def remove_all_spaces(text):
    return re.sub(r"\s+", "", text)


def type_into_input_element(input_element, text):
    input_element.send_keys(Keys.CONTROL, "a")
    input_element.send_keys(Keys.DELETE)
    enter_value_fake_slowly(0.05, 0.2, input_element, text)


def handle_reservation_popup_window(user_profile, driver):
    # Locate the div element with text 'Contact Info'
    # contact_info_div = driver.find_element("xpath", "//div[text()='Contact Info']")
    contact_info_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[text()='Contact Info']"))
    )
    # Locate the next sibling div after the 'Contact Info' div
    next_sibling_div = contact_info_div.find_element("xpath", "following-sibling::div")

    next_sibling_div.click()
    logger.info("Clicked to edit contact info")

    def handle_edit_contact_info_popup(user_profile, driver):
        email = user_profile["user_email"]
        phone_number = user_profile["user_phone"]
        first_name = user_profile["first_name"]
        last_name = user_profile["last_name"]
        timeout = 10
        # Wait for the 'First name' input to be present and then get it
        first_name_input = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@aria-label='First name']")
            )
        )
        logger.info("First name found")
        # Wait for the 'Last name' input to be present and then get it
        last_name_input = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@aria-label='Last name']")
            )
        )

        # Wait for the 'Phone number' input to be present and then get it
        phone_number_input = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@aria-label='Phone number']")
            )
        )
        email_editable_bool = False
        # Wait for the 'Email' input to be present and then get it
        try:
            # Wait until an input with aria-label='Email' is present and editable
            email_input = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@aria-label='Email' and not(@disabled)]")
                )
            )

            # Verify that the element is not disabled and can be edited
            if email_input.get_attribute("disabled") is None:
                logger.info("user email can be entered")
                email_editable_bool = True
            else:
                # raise EmailInputNotAvailableException("No editable email input found.")
                logger.info("Email not editable")
        except TimeoutException:
            # raise EmailInputNotAvailableException("No editable email input found.")
            logger.info("Email not editable")

        # Wait for the 'Update info' button to be present and then get it
        update_info_button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[descendant-or-self::*[contains(text(), 'Update info')]]",
                )
            )
        )
        generate_random_sleep_time(1.2, 5)
        type_into_input_element(first_name_input, first_name)
        generate_random_sleep_time(0.6, 1.2)
        type_into_input_element(last_name_input, last_name)
        generate_random_sleep_time(0.6, 1.2)
        type_into_input_element(phone_number_input, phone_number)
        if email_editable_bool:
            generate_random_sleep_time(0.6, 1.2)
            type_into_input_element(email_input, email)
        generate_random_sleep_time(1.5, 3)
        logger.info("next line is click update_info button")
        update_info_button.click()
    try:
        handle_edit_contact_info_popup(user_profile, driver)
    except TimeoutException as e:
        # Handle the case where the element did not appear
        logger.info(f"A input window is not found popup not found: {e} ")
    logger.info("we finished handle_edit_contact_info_popup")
    time.sleep(5)
    try:
        final_reserve_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[descendant-or-self::*[contains(text(), 'Reserve')]]",
                )
            )
        )
    except TimeoutException as e:
        # Handle the case where the element did not appear
        raise FinalReserveBtnNotAvailableException

    final_reserve_button.click()
    time.sleep(10)


def handle_continue_with_popup(driver):
    try:
        opentable_div = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[text()='Continue with']"))
        )
        logger.info("Found a continue_with popup")
    except TimeoutException:
        # Handle the case where the element did not appear
        logger.info("Continue-with popup not found, continuing without handling it.")
        return
    try:
        # Wait for the element to appear and click it if found
        opentable_div = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//div[text()='OpenTable']"))
        )
        # Perform any action you need, e.g., clicking on the popup
        opentable_div.click()
        print("OpenTable selected for continue-with popup.")
    except TimeoutException:
        # Handle the case where the element did not appear
        logger.info("OpenTable option not found in continue with popup.")
    try:
        # Wait for the element to appear and click it if found
        yelp_div = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//div[text()='Yelp']"))
        )
        # Perform any action you need, e.g., clicking on the popup
        yelp_div.click()
        print("yelp selected for continue-with popup.")
    except TimeoutException:
        # Handle the case where the element did not appear
        logger.info("Yelp option not found in continue with popup.")
    try:
        any_provider_div_to_click = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'LjLQOe') and contains(@class, 'YW5Lhe')]"))
        )
        any_provider_div_to_click.click()
    except TimeoutException:
        logger.error("No provider option found in after Continue with pop up is presented.")
        raise UnexpectedScriptError(
            "No provider option found in after Continue with pop up is presented."
        )
    

# def get_availiable_time_slots(restaurant_name, date_selection, user_email="donnahello725@gmail.com", user_phone="+16143120820", first_name="John", last_name="Jio", date_time_requirements="Make reservation for me for 3 people in total on friday of next week at 6:30PM at Osteria Toscana."):
def reserve_a_table(
        needed_info,
    user_email="chujames665@gmail.com",
    user_phone="+16143120640",
    first_name="James",
    last_name="Chu"
):
    
    driver = initializeUcDriver_with_user_profile()

    user_profile = {
        "user_email": user_email,
        "user_phone": user_phone,
        "first_name": first_name,
        "last_name": last_name,
    }
    success_notes = ""
    notes = ""
    try:
        failed_reason = ""
        # date_time_requirements="I have 3 people in total. Make reservation for me for 3 people in total on the first friday of 2025 at 6:30PM at Osteria Toscana."
        # date_time_requirements="Make reservation for me for 5 people in total on Oct 3rd at 6:30PM at Osteria Toscana."
        # city = "palo alto"
        city = "san francisco"
        # party_size = gpt_api_calls.get_party_size(date_time_requirements)
        # reservation_time = gpt_api_calls.get_reservation_time(date_time_requirements)
        # json_response = gpt_api_calls.get_date(date_time_requirements)
        # reservation_date = json_response['reservation_date']
        # reservation_year = json_response['year']
        # restaurant_name = gpt_api_calls.get_restaurant_name(date_time_requirements)

        # reservation_time = "18:30"
        restaurant_name = needed_info["restaurant_name"]
        party_size = needed_info["party_size"]
        date_selection = needed_info["date"]
        reservation_time = needed_info["time"]
        # reservation_time = time_selection
        reservation_date = date_selection["reservation_date"]
        reservation_year = date_selection["year"]
        # restaurant_name = gpt_api_calls.get_restaurant_name(date_time_requirements)

        reservation_time_12hr = convert_24hr_to_12hr(reservation_time)
        logger.info(f"({type(party_size)})party_size: {party_size}")
        logger.info(f"({type(reservation_time)})reservation_time: {reservation_time}")
        logger.info(f"({type(reservation_date)})reservation_date: {reservation_date}")
        logger.info(f"({type(reservation_year)})reservation_year: {reservation_year}")

        driver.maximize_window()

        def generate_google_maps_search_url(restaurant_name, city):
            base_url = "https://www.google.com/maps/search/?api=1&query="
            formatted_query = urllib.parse.quote(f"{restaurant_name} {city}")
            return f"{base_url}{formatted_query}"

        # Terún has back patio, indoor

        driver.get(generate_google_maps_search_url(restaurant_name, city))
        # driver.get('https://www.google.com/maps/search/?api=1&query=Osteria+Toscana+palo+alto')
        # Use XPath to locate the <a> element containing the text "Reserve a table"
        wait = WebDriverWait(driver, 10)
        try:
            reserve_link = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[.//div[contains(text(), 'Reserve a table')]]")
                )
            )
            # Click the Reserve a table element
            reserve_link.click()
        except TimeoutException:
            driver.quit()
            return {
                "status": "failed",
                "reason": "No Reserve a table button",
                "notes": notes,
            }

        click_party_size_dropdown(wait, party_size)
        # loading wait after selecting a filter question
        time.sleep(5)
        click_date_dropdown(wait, reservation_date, reservation_year, driver)
        time.sleep(5)
        click_time_dropdown(wait, reservation_time)
        time.sleep(5)

        logger.info("finished selecting filters")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='XiHZgc']"))
            )
        except TimeoutException as e:
            try:
                no_timeslots_reason = (
                    WebDriverWait(driver, 10)
                    .until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@jsname="e4SXRb"]')
                        )
                    )
                    .text
                )
                raise TimeSlotsNotFoundException(no_timeslots_reason)
            except (TimeoutException, NoSuchElementException) as inner_exception:
                # Handle the situation where the '//*[@jsname="e4SXRb"]' element is also not found
                raise TimeSlotsNotFoundException(
                    "Unable to find time slots or reason text."
                )
        parent_div = driver.find_element(By.XPATH, "//div[@class='XiHZgc']")
        logger.info("we found XiHZgc")
        child_divs = parent_div.find_elements(By.XPATH, "./div")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='C9prBc']"))
            )
        except TimeoutException as e:
            try:
                no_timeslots_reason = (
                    WebDriverWait(driver, 10)
                    .until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@jsname="e4SXRb"]')
                        )
                    )
                    .text
                )
                raise TimeSlotsNotFoundException(no_timeslots_reason)
            except (TimeoutException, NoSuchElementException) as inner_exception:
                # Handle the situation where the '//*[@jsname="e4SXRb"]' element is also not found
                raise TimeSlotsNotFoundException(
                    "Unable to find time slots or reason text."
                )
        divs_includes_all_slots_spans = driver.find_elements(
            By.XPATH, "//div[@class='C9prBc']"
        )
        all_seating_sections = {}
        chatgpt_input = ""
        substitude_avaliable_slot = None
        click_next_one_avaliable = False
        for div in divs_includes_all_slots_spans:
            # ask for all avaliable timeslots in plus minus window in all sections with section names
            parent_element = div.find_element(By.XPATH, "..")
            first_child = parent_element.find_element(By.XPATH, "./*[1]")
            seating_section_title = first_child.text
            all_seating_sections[seating_section_title] = []
            time_slots = div.find_elements(By.XPATH, "./span")
            for span in time_slots:
                try:
                    # Locate the button element within the span
                    # button = span.find_element(By.TAG_NAME, "button")
                    button = span.find_element(By.XPATH, ".//button")
                    # Extract the time slot value from the span's inner text
                    time_slot_text = button.find_element(By.TAG_NAME, "span").text
                    is_available = not button.get_attribute(
                            "disabled"
                        )  # True if not disabled, False if disabled
                    if is_available:
                        if click_next_one_avaliable:
                            if substitude_avaliable_slot:
                                substitude_avaliable_slot.click()
                                logger.info(
                                    f"Clicked substitution: {remove_all_spaces(time_slot_text)} in {seating_section_title}"
                                )
                            else:
                                button.click()
                            generate_random_sleep_time(3, 5)
                            try:
                                handle_continue_with_popup(driver)
                            except OpenTableOptionNotFoundException as e:
                                driver.quit()
                                return {
                                    "status": "failed",
                                    "reason": "OpenTable option not available in Google map",
                                    "notes": notes,
                                }
                            generate_random_sleep_time(3, 5)
                            try:
                                handle_reservation_popup_window(
                                    user_profile, driver
                                )
                            except EmailInputNotAvailableException as e:
                                driver.quit()
                                return {
                                    "status": "failed",
                                    "reason": str(e),
                                    "notes": notes,
                                }

                            def wait_for_confirmation():
                                try:
                                    # Wait up to 20 seconds for the element to appear
                                    confirmation_div = WebDriverWait(driver, 20).until(
                                        EC.presence_of_element_located(
                                            (
                                                By.XPATH,
                                                "//div[text()='Reservation confirmed']",
                                            )
                                        )
                                    )
                                    print("Reservation confirmed element found!")
                                    return confirmation_div
                                except TimeoutException:
                                    print(
                                        "Timeout: Reservation confirmed element not found within the given time."
                                    )
                                    return None

                            confirmation_div = wait_for_confirmation()
                            if confirmation_div:
                                driver.quit()
                                return {"status": "success", "notes": notes}
                            # element = driver.find_element(By.XPATH, "//div[text()='Reservation confirmed']")
                        else:
                            if remove_all_spaces(time_slot_text) == remove_all_spaces(reservation_time_12hr):
                                button.click()
                                logger.info(
                                f"Clicked exact timeslot: {remove_all_spaces(time_slot_text)} in {seating_section_title}"
                                )
                                generate_random_sleep_time(3, 5)
                                try:
                                    handle_continue_with_popup(driver)
                                except OpenTableOptionNotFoundException as e:
                                    driver.quit()
                                    return {
                                        "status": "failed",
                                        "reason": "OpenTable option not available in Google map",
                                        "notes": notes,
                                    }
                                generate_random_sleep_time(3, 5)
                                try:
                                    handle_reservation_popup_window(
                                        user_profile, driver
                                    )
                                except EmailInputNotAvailableException as e:
                                    driver.quit()
                                    return {
                                        "status": "failed",
                                        "reason": str(e),
                                        "notes": notes,
                                    }

                                def wait_for_confirmation():
                                    try:
                                        # Wait up to 20 seconds for the element to appear
                                        confirmation_div = WebDriverWait(driver, 20).until(
                                            EC.presence_of_element_located(
                                                (
                                                    By.XPATH,
                                                    "//div[text()='Reservation confirmed']",
                                                )
                                            )
                                        )
                                        print("Reservation confirmed element found!")
                                        return confirmation_div
                                    except TimeoutException:
                                        print(
                                            "Timeout: Reservation confirmed element not found within the given time."
                                        )
                                        return None

                                confirmation_div = wait_for_confirmation()
                                if confirmation_div:
                                    driver.quit()
                                    return {"status": "success", "notes": notes}
                            else:
                                substitude_avaliable_slot = button
                                
                            
                        all_seating_sections[seating_section_title].append(time_slot_text)
                    else:
                        if remove_all_spaces(time_slot_text) == remove_all_spaces(reservation_time_12hr):
                            click_next_one_avaliable = True

                except Exception as e:
                    logger.exception(e)
                    driver.quit()
                    print(f"Uncatched error when trying to find a timeslot: {e}")
            

            # for div in divs_includes_all_slots_spans:
        #     seating_section_title = "Default seating section(Indoor)"
        #     if len(divs_includes_all_slots_spans) > 1:
        #         parent_element = div.find_element(By.XPATH, "..")
        #         first_child = parent_element.find_element(By.XPATH, "./*[1]")
        #         seating_section_title = first_child.text
        #         notes += "Seating sections found. "
        #         print("")
        #     time_slots = div.find_elements(By.XPATH, "./span")
        #     exactly_same_time = True
        #     for span in time_slots:
        #         try:
        #             # Locate the button element within the span
        #             button = span.find_element(By.TAG_NAME, "button")

        #             # Extract the time slot value from the span's inner text
        #             time_slot_text = button.find_element(By.TAG_NAME, "span").text
        #             # logger.info(f"match? time_slot_text: {time_slot_text}")
        #             if remove_all_spaces(time_slot_text) == remove_all_spaces(
        #                 reservation_time_12hr
        #             ):
        #                 # Check if the button has the 'disabled' attribute
        #                 # logger.info(f"matched {time_slot_text}")
        #                 is_available = not button.get_attribute(
        #                     "disabled"
        #                 )  # True if not disabled, False if disabled
        #                 if is_available:
        #                     button.click()
        #                     logger.info(
        #                         f"Clicked {remove_all_spaces(time_slot_text)} in {seating_section_title}"
        #                     )
        #                     generate_random_sleep_time(3, 5)
        #                     try:
        #                         handle_continue_with_popup(driver)
        #                     except OpenTableOptionNotFoundException as e:
        #                         driver.quit()
        #                         return {
        #                             "status": "failed",
        #                             "reason": "OpenTable option not available in Google map",
        #                             "notes": notes,
        #                         }
        #                     generate_random_sleep_time(3, 5)
        #                     try:
        #                         handle_reservation_popup_window(
        #                             user_profile=user_profile
        #                         )
        #                     except EmailInputNotAvailableException as e:
        #                         driver.quit()
        #                         return {
        #                             "status": "failed",
        #                             "reason": str(e),
        #                             "notes": notes,
        #                         }

        #                     def wait_for_confirmation():
        #                         try:
        #                             # Wait up to 20 seconds for the element to appear
        #                             confirmation_div = WebDriverWait(driver, 20).until(
        #                                 EC.presence_of_element_located(
        #                                     (
        #                                         By.XPATH,
        #                                         "//div[text()='Reservation confirmed']",
        #                                     )
        #                                 )
        #                             )
        #                             print("Reservation confirmed element found!")
        #                             return confirmation_div
        #                         except TimeoutException:
        #                             print(
        #                                 "Timeout: Reservation confirmed element not found within the given time."
        #                             )
        #                             return None

        #                     confirmation_div = wait_for_confirmation()
        #                     if confirmation_div:
        #                         driver.quit()
        #                         return {"status": "success", "notes": notes}
        #                     # element = driver.find_element(By.XPATH, "//div[text()='Reservation confirmed']")
        #                 else:
        #                     exactly_same_time = False
        #                     driver.quit()
        #                     return {
        #                         "status": "failed",
        #                         "reason": "Exact same time slot is not available",
        #                         "notes": notes,
        #                     }
        #                     # Return all the available time slots available and ask again
        #                     # For test run, we select any one that is available

        #         except Exception as e:
        #             logger.exception(e)
        #             driver.quit()
        #             print(f"Error while processing a time slot: {e}")
        driver.quit()
        return {
            "status": "failed",
            "reason": "reached the end of the script",
            "notes": notes + "reached the end of the script",
        }
    except DateUnavailableException as e:
        logger.exception(e)
        driver.quit()
        return {"status": "failed", "reason": str(e), "notes": notes}
    except FinalReserveBtnNotAvailableException as e:
        driver.quit()
        return {"status": "failed", "reason": str(e), "notes": notes}
    except TimeUnavailableException as e:
        driver.quit()
        return {"status": "failed", "reason": str(e), "notes": notes}
    except UnexpectedScriptError as e:
        driver.quit()
        return {"status": "failed", "reason": str(e), "notes": notes}
    except TimeSlotsNotFoundException as e:
        driver.quit()
        return {"status": "failed", "reason": str(e.message), "notes": notes}
    # except Exception as e:
    #     driver.quit()
    #     return {
    #         "status": "failed",
    #         "reason": f"Unhandled error: {str(e)}",
    #         "notes": success_notes,
    #     }

def reserve_a_table_asking_seating(
        needed_info,
    user_email="chujames665@gmail.com",
    user_phone="+16143120640",
    first_name="James",
    last_name="Chu"
):
    
    driver = initializeUcDriver_with_user_profile()

    user_profile = {
        "user_email": user_email,
        "user_phone": user_phone,
        "first_name": first_name,
        "last_name": last_name,
    }
    success_notes = ""
    notes = ""
    try:
        failed_reason = ""
        # date_time_requirements="I have 3 people in total. Make reservation for me for 3 people in total on the first friday of 2025 at 6:30PM at Osteria Toscana."
        # date_time_requirements="Make reservation for me for 5 people in total on Oct 3rd at 6:30PM at Osteria Toscana."
        # city = "palo alto"
        city = "san francisco"
        # party_size = gpt_api_calls.get_party_size(date_time_requirements)
        # reservation_time = gpt_api_calls.get_reservation_time(date_time_requirements)
        # json_response = gpt_api_calls.get_date(date_time_requirements)
        # reservation_date = json_response['reservation_date']
        # reservation_year = json_response['year']
        # restaurant_name = gpt_api_calls.get_restaurant_name(date_time_requirements)

        # reservation_time = "18:30"
        restaurant_name = needed_info["restaurant_name"]
        party_size = needed_info["party_size"]
        date_selection = needed_info["date"]
        reservation_time = needed_info["time"]
        # reservation_time = time_selection
        reservation_date = date_selection["reservation_date"]
        reservation_year = date_selection["year"]
        # restaurant_name = gpt_api_calls.get_restaurant_name(date_time_requirements)

        reservation_time_12hr = convert_24hr_to_12hr(reservation_time)
        logger.info(f"({type(party_size)})party_size: {party_size}")
        logger.info(f"({type(reservation_time)})reservation_time: {reservation_time}")
        logger.info(f"({type(reservation_date)})reservation_date: {reservation_date}")
        logger.info(f"({type(reservation_year)})reservation_year: {reservation_year}")

        driver.maximize_window()

        def generate_google_maps_search_url(restaurant_name, city):
            base_url = "https://www.google.com/maps/search/?api=1&query="
            formatted_query = urllib.parse.quote(f"{restaurant_name} {city}")
            return f"{base_url}{formatted_query}"

        # Terún has back patio, indoor

        driver.get(generate_google_maps_search_url(restaurant_name, city))
        # driver.get('https://www.google.com/maps/search/?api=1&query=Osteria+Toscana+palo+alto')
        # Use XPath to locate the <a> element containing the text "Reserve a table"
        wait = WebDriverWait(driver, 10)
        try:
            reserve_link = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[.//div[contains(text(), 'Reserve a table')]]")
                )
            )
            # Click the Reserve a table element
            reserve_link.click()
        except TimeoutException:
            driver.quit()
            return {
                "status": "failed",
                "reason": "No Reserve a table button",
                "notes": notes,
            }

        click_party_size_dropdown(wait, party_size)
        # loading wait after selecting a filter question
        time.sleep(5)
        click_date_dropdown(wait, reservation_date, reservation_year, driver)
        time.sleep(5)
        click_time_dropdown(wait, reservation_time)
        time.sleep(5)

        logger.info("finished selecting filters")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='XiHZgc']"))
            )
        except TimeoutException as e:
            try:
                no_timeslots_reason = (
                    WebDriverWait(driver, 10)
                    .until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@jsname="e4SXRb"]')
                        )
                    )
                    .text
                )
                raise TimeSlotsNotFoundException(no_timeslots_reason)
            except (TimeoutException, NoSuchElementException) as inner_exception:
                # Handle the situation where the '//*[@jsname="e4SXRb"]' element is also not found
                raise TimeSlotsNotFoundException(
                    "Unable to find time slots or reason text."
                )
        parent_div = driver.find_element(By.XPATH, "//div[@class='XiHZgc']")
        logger.info("we found XiHZgc")
        child_divs = parent_div.find_elements(By.XPATH, "./div")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='C9prBc']"))
            )
        except TimeoutException as e:
            try:
                no_timeslots_reason = (
                    WebDriverWait(driver, 10)
                    .until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@jsname="e4SXRb"]')
                        )
                    )
                    .text
                )
                raise TimeSlotsNotFoundException(no_timeslots_reason)
            except (TimeoutException, NoSuchElementException) as inner_exception:
                # Handle the situation where the '//*[@jsname="e4SXRb"]' element is also not found
                raise TimeSlotsNotFoundException(
                    "Unable to find time slots or reason text."
                )
        divs_includes_all_slots_spans = driver.find_elements(
            By.XPATH, "//div[@class='C9prBc']"
        )
        all_seating_sections = {}
        chatgpt_input = ""
        if len(divs_includes_all_slots_spans) > 1:
            for div in divs_includes_all_slots_spans:
                # ask for all avaliable timeslots in plus minus window in all sections with section names
                parent_element = div.find_element(By.XPATH, "..")
                first_child = parent_element.find_element(By.XPATH, "./*[1]")
                seating_section_title = first_child.text
                all_seating_sections[seating_section_title] = []
                time_slots = div.find_elements(By.XPATH, "./span")
                for span in time_slots:
                    try:
                        # Locate the button element within the span
                        # button = span.find_element(By.TAG_NAME, "button")
                        button = span.find_element(By.XPATH, ".//button")
                        # Extract the time slot value from the span's inner text
                        time_slot_text = button.find_element(By.TAG_NAME, "span").text
                        is_available = not button.get_attribute(
                                "disabled"
                            )  # True if not disabled, False if disabled
                        if is_available:
                            all_seating_sections[seating_section_title].append(time_slot_text)
            

                    except Exception as e:
                        logger.exception(e)
                        driver.quit()
                        print(f"Uncatched error when trying to find a timeslot: {e}")
            seating_section_ask_str = f"Donna: I found the following available reservation times at {restaurant_name} for {reservation_date}. Please specify which time slot and seating section you want to reserve:\n\n"

            for section, timeslots in all_seating_sections.items():
                # Add seating section and timeslots to the string
                single_seating_section_str = f"Seating Section: {section}\n"
                if timeslots:
                    # Join timeslots with commas for readability
                    single_seating_section_str += f"Available Timeslots: {', '.join(timeslots)}\n"
                    for timeslot in timeslots:
                        if remove_all_spaces(reservation_time_12hr) == remove_all_spaces(timeslot):
                            single_seating_section_str = f"Seating Section: {section}\n{timeslot}\n"
                            break
                else:
                    single_seating_section_str += "No available timeslots\n"
                seating_section_ask_str += single_seating_section_str
                seating_section_ask_str += "\n"  # Blank line between sections for clarity

            # Print or return the final formatted string
            print(seating_section_ask_str)
            chatgpt_input = seating_section_ask_str
            gpt_response = ""
            while not gpt_response:
                print(seating_section_ask_str)
                chatgpt_input = seating_section_ask_str
                user_input = input("Please enter user message (type 'exit' to quit): ")
                gpt_response = gpt_api_calls.get_selected_time_slot(chatgpt_input + "\n" + user_input)                
            for div in divs_includes_all_slots_spans:
                time_slots = div.find_elements(By.XPATH, "./span")
                for span in time_slots:
                    try:
                        # Locate the button element within the span
                        # button = span.find_element(By.TAG_NAME, "button")
                        button = span.find_element(By.XPATH, ".//button")
                        # Extract the time slot value from the span's inner text
                        time_slot_text = button.find_element(By.TAG_NAME, "span").text
                        # logger.info(f"match? time_slot_text: {time_slot_text}")
                        if remove_all_spaces(time_slot_text) == remove_all_spaces(
                            gpt_response
                        ):
                            # Check if the button has the 'disabled' attribute
                            # logger.info(f"matched {time_slot_text}")
                            is_available = not button.get_attribute(
                                "disabled"
                            )  # True if not disabled, False if disabled
                            if is_available:
                                button.click()
                                # logger.info(
                                #     f"Clicked {remove_all_spaces(time_slot_text)} in {seating_section_title}"
                                # )
                                generate_random_sleep_time(3, 5)
                                try:
                                    handle_continue_with_popup(driver)
                                except OpenTableOptionNotFoundException as e:
                                    driver.quit()
                                    return {
                                        "status": "failed",
                                        "reason": "OpenTable option not available in Google map",
                                        "notes": notes,
                                    }
                                generate_random_sleep_time(3, 5)
                                try:
                                    handle_reservation_popup_window(
                                        user_profile, driver
                                    )
                                except EmailInputNotAvailableException as e:
                                    driver.quit()
                                    return {
                                        "status": "failed",
                                        "reason": str(e),
                                        "notes": notes,
                                    }

                                def wait_for_confirmation():
                                    try:
                                        # Wait up to 20 seconds for the element to appear
                                        confirmation_div = WebDriverWait(driver, 20).until(
                                            EC.presence_of_element_located(
                                                (
                                                    By.XPATH,
                                                    "//div[text()='Reservation confirmed']",
                                                )
                                            )
                                        )
                                        print("Reservation confirmed element found!")
                                        return confirmation_div
                                    except TimeoutException:
                                        print(
                                            "Timeout: Reservation confirmed element not found within the given time."
                                        )
                                        return None

                                confirmation_div = wait_for_confirmation()
                                if confirmation_div:
                                    driver.quit()
                                    return {"status": "success", "notes": notes}
                                # element = driver.find_element(By.XPATH, "//div[text()='Reservation confirmed']")
                            else:
                                exactly_same_time = False
                                driver.quit()
                                return {
                                    "status": "failed",
                                    "reason": "Exact same time slot is not available",
                                    "notes": notes,
                                }
                                # Return all the available time slots available and ask again
                                # For test run, we select any one that is available

                    except Exception as e:
                        logger.exception(e)
                        driver.quit()
                        print(f"Error while processing a time slot: {e}")
        else:
            print(f"else condition: len(divs_includes_all_slots_spans): {len(divs_includes_all_slots_spans)}")
            for div in divs_includes_all_slots_spans:
                seating_section_title = 'only_seating_section'
                all_seating_sections[seating_section_title] = []
                time_slots = div.find_elements(By.XPATH, "./span")
                for span in time_slots:
                    try:
                        # Locate the button element within the span
                        # button = span.find_element(By.TAG_NAME, "button")
                        button = span.find_element(By.XPATH, ".//button")
                        # Extract the time slot value from the span's inner text
                        time_slot_text = button.find_element(By.TAG_NAME, "span").text
                        is_available = not button.get_attribute(
                                "disabled"
                            )  # True if not disabled, False if disabled
                        if is_available:
                            all_seating_sections[seating_section_title].append(time_slot_text)

                    except Exception as e:
                        logger.exception(e)
                        driver.quit()
                        print(f"Uncatched error when trying to find a timeslot: {e}")
            seating_section_ask_str = f"Donna: The exact time slot you requested was not avaliable, I found the following available reservation times at {restaurant_name} for {reservation_date}. Please specify which time slot you want to reserve instead:\n\n"
            for section, timeslots in all_seating_sections.items():
                # Add seating section and timeslots to the string
                if timeslots:
                    seating_section_ask_str += f"Available Timeslots: {', '.join(timeslots)}\n"
                    # Join timeslots with commas for readability
                    for timeslot in timeslots:
                        if remove_all_spaces(reservation_time_12hr) == remove_all_spaces(timeslot):
                            print("pick because no seating section needed")
                            for div in divs_includes_all_slots_spans:
                                time_slots = div.find_elements(By.XPATH, "./span")
                                for span in time_slots:
                                    try:
                                        # Locate the button element within the span
                                        # button = span.find_element(By.TAG_NAME, "button")
                                        button = span.find_element(By.XPATH, ".//button")
                                        # Extract the time slot value from the span's inner text
                                        time_slot_text = button.find_element(By.TAG_NAME, "span").text
                                        # logger.info(f"match? time_slot_text: {time_slot_text}")
                                        if remove_all_spaces(time_slot_text) == remove_all_spaces(
                                            reservation_time_12hr
                                        ):
                                            # Check if the button has the 'disabled' attribute
                                            # logger.info(f"matched {time_slot_text}")
                                            is_available = not button.get_attribute(
                                                "disabled"
                                            )  # True if not disabled, False if disabled
                                            if is_available:
                                                button.click()
                                                logger.info(
                                                    f"Clicked {remove_all_spaces(time_slot_text)} in {seating_section_title}"
                                                )
                                                generate_random_sleep_time(3, 5)
                                                try:
                                                    handle_continue_with_popup(driver)
                                                except OpenTableOptionNotFoundException as e:
                                                    driver.quit()
                                                    return {
                                                        "status": "failed",
                                                        "reason": "OpenTable option not available in Google map",
                                                        "notes": notes,
                                                    }
                                                generate_random_sleep_time(3, 5)
                                                try:
                                                    handle_reservation_popup_window(
                                                        user_profile, driver
                                                    )
                                                except EmailInputNotAvailableException as e:
                                                    driver.quit()
                                                    return {
                                                        "status": "failed",
                                                        "reason": str(e),
                                                        "notes": notes,
                                                    }

                                                def wait_for_confirmation():
                                                    try:
                                                        # Wait up to 20 seconds for the element to appear
                                                        confirmation_div = WebDriverWait(driver, 20).until(
                                                            EC.presence_of_element_located(
                                                                (
                                                                    By.XPATH,
                                                                    "//div[text()='Reservation confirmed']",
                                                                )
                                                            )
                                                        )
                                                        print("Reservation confirmed element found!")
                                                        return confirmation_div
                                                    except TimeoutException:
                                                        print(
                                                            "Timeout: Reservation confirmed element not found within the given time."
                                                        )
                                                        return None

                                                confirmation_div = wait_for_confirmation()
                                                if confirmation_div:
                                                    driver.quit()
                                                    return {"status": "success", "notes": notes}
                                                # element = driver.find_element(By.XPATH, "//div[text()='Reservation confirmed']")
                                            else:
                                                exactly_same_time = False
                                                driver.quit()
                                                return {
                                                    "status": "failed",
                                                    "reason": "Exact same time slot is not available",
                                                    "notes": notes,
                                                }
                                                # Return all the available time slots available and ask again
                                                # For test run, we select any one that is available

                                    except Exception as e:
                                        logger.exception(e)
                                        driver.quit()
                                        print(f"Error while processing a time slot: {e}")
                            return
            seating_section_ask_str += "\n"  # Blank line between sections for clarity

            # Print or return the final formatted string

            gpt_response = ""
            while not gpt_response:
                print(seating_section_ask_str)
                chatgpt_input = seating_section_ask_str
                user_input = input("Please enter user message (type 'exit' to quit): ")
                gpt_response = gpt_api_calls.get_selected_time_slot(chatgpt_input + "\n" + user_input)                
            for div in divs_includes_all_slots_spans:
                time_slots = div.find_elements(By.XPATH, "./span")
                for span in time_slots:
                    try:
                        # Locate the button element within the span
                        # button = span.find_element(By.TAG_NAME, "button")
                        button = span.find_element(By.XPATH, ".//button")
                        # Extract the time slot value from the span's inner text
                        time_slot_text = button.find_element(By.TAG_NAME, "span").text
                        # logger.info(f"match? time_slot_text: {time_slot_text}")
                        if remove_all_spaces(time_slot_text) == remove_all_spaces(
                            gpt_response
                        ):
                            # Check if the button has the 'disabled' attribute
                            # logger.info(f"matched {time_slot_text}")
                            is_available = not button.get_attribute(
                                "disabled"
                            )  # True if not disabled, False if disabled
                            if is_available:
                                button.click()
                                # logger.info(
                                #     f"Clicked {remove_all_spaces(time_slot_text)} in {seating_section_title}"
                                # )
                                generate_random_sleep_time(3, 5)
                                try:
                                    handle_continue_with_popup(driver)
                                except OpenTableOptionNotFoundException as e:
                                    driver.quit()
                                    return {
                                        "status": "failed",
                                        "reason": "OpenTable option not available in Google map",
                                        "notes": notes,
                                    }
                                generate_random_sleep_time(3, 5)
                                try:
                                    handle_reservation_popup_window(
                                        user_profile, driver
                                    )
                                except EmailInputNotAvailableException as e:
                                    driver.quit()
                                    return {
                                        "status": "failed",
                                        "reason": str(e),
                                        "notes": notes,
                                    }

                                def wait_for_confirmation():
                                    try:
                                        # Wait up to 20 seconds for the element to appear
                                        confirmation_div = WebDriverWait(driver, 20).until(
                                            EC.presence_of_element_located(
                                                (
                                                    By.XPATH,
                                                    "//div[text()='Reservation confirmed']",
                                                )
                                            )
                                        )
                                        print("Reservation confirmed element found!")
                                        return confirmation_div
                                    except TimeoutException:
                                        print(
                                            "Timeout: Reservation confirmed element not found within the given time."
                                        )
                                        return None

                                confirmation_div = wait_for_confirmation()
                                if confirmation_div:
                                    driver.quit()
                                    return {"status": "success", "notes": notes}
                                # element = driver.find_element(By.XPATH, "//div[text()='Reservation confirmed']")
                            else:
                                exactly_same_time = False
                                driver.quit()
                                return {
                                    "status": "failed",
                                    "reason": "Exact same time slot is not available",
                                    "notes": notes,
                                }
                                # Return all the available time slots available and ask again
                                # For test run, we select any one that is available

                    except Exception as e:
                        logger.exception(e)
                        driver.quit()
                        print(f"Error while processing a time slot: {e}")
        # for div in divs_includes_all_slots_spans:
        #     seating_section_title = "Default seating section(Indoor)"
        #     if len(divs_includes_all_slots_spans) > 1:
        #         parent_element = div.find_element(By.XPATH, "..")
        #         first_child = parent_element.find_element(By.XPATH, "./*[1]")
        #         seating_section_title = first_child.text
        #         notes += "Seating sections found. "
        #         print("")
        #     time_slots = div.find_elements(By.XPATH, "./span")
        #     exactly_same_time = True
        #     for span in time_slots:
        #         try:
        #             # Locate the button element within the span
        #             button = span.find_element(By.TAG_NAME, "button")

        #             # Extract the time slot value from the span's inner text
        #             time_slot_text = button.find_element(By.TAG_NAME, "span").text
        #             # logger.info(f"match? time_slot_text: {time_slot_text}")
        #             if remove_all_spaces(time_slot_text) == remove_all_spaces(
        #                 reservation_time_12hr
        #             ):
        #                 # Check if the button has the 'disabled' attribute
        #                 # logger.info(f"matched {time_slot_text}")
        #                 is_available = not button.get_attribute(
        #                     "disabled"
        #                 )  # True if not disabled, False if disabled
        #                 if is_available:
        #                     button.click()
        #                     logger.info(
        #                         f"Clicked {remove_all_spaces(time_slot_text)} in {seating_section_title}"
        #                     )
        #                     generate_random_sleep_time(3, 5)
        #                     try:
        #                         handle_continue_with_popup(driver)
        #                     except OpenTableOptionNotFoundException as e:
        #                         driver.quit()
        #                         return {
        #                             "status": "failed",
        #                             "reason": "OpenTable option not available in Google map",
        #                             "notes": notes,
        #                         }
        #                     generate_random_sleep_time(3, 5)
        #                     try:
        #                         handle_reservation_popup_window(
        #                             user_profile=user_profile
        #                         )
        #                     except EmailInputNotAvailableException as e:
        #                         driver.quit()
        #                         return {
        #                             "status": "failed",
        #                             "reason": str(e),
        #                             "notes": notes,
        #                         }

        #                     def wait_for_confirmation():
        #                         try:
        #                             # Wait up to 20 seconds for the element to appear
        #                             confirmation_div = WebDriverWait(driver, 20).until(
        #                                 EC.presence_of_element_located(
        #                                     (
        #                                         By.XPATH,
        #                                         "//div[text()='Reservation confirmed']",
        #                                     )
        #                                 )
        #                             )
        #                             print("Reservation confirmed element found!")
        #                             return confirmation_div
        #                         except TimeoutException:
        #                             print(
        #                                 "Timeout: Reservation confirmed element not found within the given time."
        #                             )
        #                             return None

        #                     confirmation_div = wait_for_confirmation()
        #                     if confirmation_div:
        #                         driver.quit()
        #                         return {"status": "success", "notes": notes}
        #                     # element = driver.find_element(By.XPATH, "//div[text()='Reservation confirmed']")
        #                 else:
        #                     exactly_same_time = False
        #                     driver.quit()
        #                     return {
        #                         "status": "failed",
        #                         "reason": "Exact same time slot is not available",
        #                         "notes": notes,
        #                     }
        #                     # Return all the available time slots available and ask again
        #                     # For test run, we select any one that is available

        #         except Exception as e:
        #             logger.exception(e)
        #             driver.quit()
        #             print(f"Error while processing a time slot: {e}")
        driver.quit()
        return {
            "status": "failed",
            "reason": "reached the end of the script",
            "notes": notes + "reached the end of the script",
        }
    except DateUnavailableException as e:
        logger.exception(e)
        driver.quit()
        return {"status": "failed", "reason": str(e), "notes": notes}
    except FinalReserveBtnNotAvailableException as e:
        driver.quit()
        return {"status": "failed", "reason": str(e), "notes": notes}
    except TimeUnavailableException as e:
        driver.quit()
        return {"status": "failed", "reason": str(e), "notes": notes}
    except UnexpectedScriptError as e:
        driver.quit()
        return {"status": "failed", "reason": str(e), "notes": notes}
    except TimeSlotsNotFoundException as e:
        driver.quit()
        return {"status": "failed", "reason": str(e.message), "notes": notes}
    # except Exception as e:
    #     driver.quit()
    #     return {
    #         "status": "failed",
    #         "reason": f"Unhandled error: {str(e)}",
    #         "notes": success_notes,
    #     }


def get_all_seating_sections(restaurant_name):
    seating_section_list = []
    success_notes = ""
    notes = ""
    try:
        failed_reason = ""
        # date_time_requirements="I have 3 people in total. Make reservation for me for 3 people in total on the first friday of 2025 at 6:30PM at Osteria Toscana."
        # date_time_requirements="Make reservation for me for 5 people in total on Oct 3rd at 6:30PM at Osteria Toscana."
        city = "palo alto"
        # party_size = gpt_api_calls.get_party_size(date_time_requirements)
        # reservation_time = gpt_api_calls.get_reservation_time(date_time_requirements)
        # json_response = gpt_api_calls.get_date(date_time_requirements)
        # reservation_date = json_response['reservation_date']
        # reservation_year = json_response['year']
        # restaurant_name = gpt_api_calls.get_restaurant_name(date_time_requirements)

        party_size = "2"
        reservation_time = "18:00"
        json_response = {"reservation_date": "Wednesday, Oct 23", "year": "2024"}
        reservation_date = json_response["reservation_date"]
        reservation_year = json_response["year"]
        # restaurant_name = gpt_api_calls.get_restaurant_name(date_time_requirements)

        reservation_time_12hr = convert_24hr_to_12hr(reservation_time)

        driver.maximize_window()

        def generate_google_maps_search_url(restaurant_name, city):
            base_url = "https://www.google.com/maps/search/?api=1&query="
            formatted_query = urllib.parse.quote(f"{restaurant_name} {city}")
            return f"{base_url}{formatted_query}"

        # Terún has back patio, indoor

        driver.get(generate_google_maps_search_url(restaurant_name, city))
        # driver.get('https://www.google.com/maps/search/?api=1&query=Osteria+Toscana+palo+alto')
        # Use XPath to locate the <a> element containing the text "Reserve a table"
        wait = WebDriverWait(driver, 10)
        try:
            reserve_link = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[.//div[contains(text(), 'Reserve a table')]]")
                )
            )
            # Click the Reserve a table element
            reserve_link.click()
        except TimeoutException:
            driver.quit()
            return {
                "status": "failed",
                "reason": "No Reserve a table button",
                "notes": notes,
            }

        click_party_size_dropdown(wait, party_size)
        # loading wait after selecting a filter question
        time.sleep(5)
        click_date_dropdown(wait, reservation_date, reservation_year)
        time.sleep(5)
        click_time_dropdown(wait, reservation_time)
        time.sleep(5)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='XiHZgc']"))
            )
        except TimeoutException as e:
            try:
                no_timeslots_reason = (
                    WebDriverWait(driver, 10)
                    .until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@jsname="e4SXRb"]')
                        )
                    )
                    .text
                )
                raise TimeSlotsNotFoundException(no_timeslots_reason)
            except (TimeoutException, NoSuchElementException) as inner_exception:
                # Handle the situation where the '//*[@jsname="e4SXRb"]' element is also not found
                raise TimeSlotsNotFoundException(
                    "Unable to find time slots or reason text."
                )
        parent_div = driver.find_element(By.XPATH, "//div[@class='XiHZgc']")
        logger.info("we found XiHZgc")
        child_divs = parent_div.find_elements(By.XPATH, "./div")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='C9prBc']"))
            )
        except TimeoutException as e:
            try:
                no_timeslots_reason = (
                    WebDriverWait(driver, 10)
                    .until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@jsname="e4SXRb"]')
                        )
                    )
                    .text
                )
                raise TimeSlotsNotFoundException(no_timeslots_reason)
            except (TimeoutException, NoSuchElementException) as inner_exception:
                # Handle the situation where the '//*[@jsname="e4SXRb"]' element is also not found
                raise TimeSlotsNotFoundException(
                    "Unable to find time slots or reason text."
                )
        divs_includes_all_slots_spans = driver.find_elements(
            By.XPATH, "//div[@class='C9prBc']"
        )

        for div in divs_includes_all_slots_spans:
            seating_section_title = "Default seating section(Indoor)"
            if len(divs_includes_all_slots_spans) > 1:
                parent_element = div.find_element(By.XPATH, "..")
                first_child = parent_element.find_element(By.XPATH, "./*[1]")
                seating_section_title = first_child.text
                seating_section_list.append(seating_section_title)
                notes += "Seating sections found. "
            else:
                return []
        return seating_section_list
    except DateUnavailableException as e:
        logger.exception(e)
        driver.quit()
        return {"status": "failed", "reason": str(e), "notes": notes}
    except TimeUnavailableException as e:
        driver.quit()
        return {"status": "failed", "reason": str(e), "notes": notes}
    except UnexpectedScriptError as e:
        driver.quit()
        return {"status": "failed", "reason": str(e), "notes": notes}
    except TimeSlotsNotFoundException as e:
        driver.quit()
        return {"status": "failed", "reason": str(e.message), "notes": notes}
    except Exception as e:
        driver.quit()
        return {
            "status": "failed",
            "reason": f"Unhandled error: {str(e)}",
            "notes": success_notes,
        }



def click_date_dropdown(wait, reservation_date, reservation_year, driver):
    # Extract the target day and target month abbreviation
    target_day = reservation_date.split()[-1]  # '4'
    target_month_abbr = reservation_date.split()[1]  # 'Oct'
    target_month_year_abbr = f"{target_month_abbr} {reservation_year}"  # 'Oct 2024'

    # Convert target month abbreviation to its full name
    target_month_full = month_mapping[target_month_abbr]  # 'October'
    target_month_year_full = f"{target_month_full} {reservation_year}"  # 'October 2024'
    calendar_xpath_root = "//div[@role='region' and @aria-label='Calendar']"

    # Function to get the displayed month/year text using the root element
    def get_displayed_month_year():
        """
        Extracts the month and year text from the calendar date picker using the root container element.
        """
        # Locate the month and year element in the calendar header and return its text
        month_year_element = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"{calendar_xpath_root}//div[@jsname='xv3kgd' and @aria-live='assertive']",
                )
            )
        )
        return month_year_element.text

    # Function to click the next month button using the root element
    def click_next_month():
        """
        Clicks the next month button on the date picker using the root container element.
        """
        # Locate the "Next" button using the `aria-label` attribute and click it
        next_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"{calendar_xpath_root}//div[@aria-label='next month']")
            )
        )
        logger.debug("need to click next month, about to click")
        driver.execute_script("arguments[0].click();", next_button)

        logger.info("Clicked next month")

    # Function to select the target day using the root element
    def select_day(day):
        """
        Selects the day on the calendar using the root container element.
        """
        # Locate the day element using the `data-day-of-month` attribute and click it
        day_element = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"{calendar_xpath_root}//div[@data-day-of-month='{day}' and @role='button' and not(@aria-disabled='true')]",
                )
            )
        )
        day_element.click()

    # Step 1: Locate the parent container of the "Date" dropdown by its label
    date_dropdown_container = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[div[contains(text(), 'Date')]]")
        )
    )

    # Step 2: Find the dropdown button inside this container using role="button"
    date_dropdown_button = date_dropdown_container.find_element(
        By.XPATH, ".//div[@role='button']"
    )

    # Step 3: Click to open the dropdown menu
    date_dropdown_button.click()

    # Step 2: Wait until the calendar is visible
    calendar_container = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[@role='region' and @aria-label='Calendar']")
        )
    )
    logger.debug("We see the calendar datepicker now")
    # Step 3: Locate the day element using `data-day-of-month` attribute
    # Adjusting the XPATH to match the specific day in the visible calendar
    # Loop until the target month and year in full format are displayed
    while get_displayed_month_year() != target_month_year_full:
        logger.info(f"get_displayed_month_year(): {get_displayed_month_year()}")

        click_next_month()

    # Once the correct month and year are displayed, select the target day
    try:
        select_day(target_day)
    except TimeoutException:
        raise DateUnavailableException(
            f"Date '{target_month_year_full}, {target_day}' is unavailable for reservation."
        )


def click_party_size_dropdown(wait, party_size):
    party_size_dropdown = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[div[contains(text(), 'Party')]]")
        )
    )

    # Step 2: Find the dropdown element within the identified container
    # The dropdown element should be a div with `role="combobox"` or similar identifier
    party_size_dropdown_button = party_size_dropdown.find_element(
        By.XPATH, ".//div[@role='combobox']"
    )
    # Step 3: Click to open the dropdown
    party_size_dropdown_button.click()
    # Step 3: Wait for the dropdown options to be visible
    # Updated XPath based on the new structure, targeting the <ul> container and <li> options
    dropdown_options = wait.until(
        EC.visibility_of_all_elements_located(
            (By.XPATH, "//ul[@aria-label='Select party size']/li[@role='option']")
        )
    )
    # Step 4: Iterate through the options and select the one that matches the desired party size
    for option in dropdown_options:
        option_value = option.get_attribute(
            "data-value"
        )  # Get the value attribute of each option
        if option_value == str(
            party_size
        ):  # Compare with the desired party size (converted to string)
            option.click()
            logger.info(f"Selected party size: {party_size}")
            break


def click_time_dropdown(wait, reservation_time):
    # Step 1: Locate the "Time" dropdown container using its label
    time_dropdown_container = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[div[contains(text(), 'Time')]]")
        )
    )

    # Step 2: Find the dropdown button inside this container
    time_dropdown_button = time_dropdown_container.find_element(
        By.XPATH, ".//div[@role='combobox']"
    )

    # Step 3: Click the dropdown button to expand the menu
    time_dropdown_button.click()

    dropdown_options = wait.until(
        EC.visibility_of_all_elements_located(
            (By.XPATH, "//ul[@aria-label='Select reservation time']/li[@role='option']")
        )
    )
    # Step 4: Iterate through the options and select the one that matches the desired party size
    for option in dropdown_options:
        option_value = option.get_attribute(
            "data-value"
        )  # Get the value attribute of each option
        if option_value == str(
            reservation_time
        ):  # Compare with the desired party size (converted to string)
            option.click()
            logger.info(f"Selected party size: {reservation_time}")
            break


def scrape_availabilities(child_divs):
    time_slots_availability = {}
    for child_div in child_divs:
        # seating_section_title examples: Restaurant, Outdoor, Patios and etc.
        seating_section_title = child_div.find_element(By.XPATH, "child::*[1]").text
        print(f"{seating_section_title}")
        time_slots_availability[seating_section_title] = {}
        div_includes_all_slots_spans = child_div.find_element(By.XPATH, "child::*[2]")
        time_slots = div_includes_all_slots_spans.find_elements(By.XPATH, "./span")
        for span in time_slots:
            try:
                # Locate the button element within the span
                # button = span.find_element(By.TAG_NAME, "button")
                button = span.find_element(By.XPATH, ".//button")
                # Extract the time slot value from the span's inner text
                time_slot_text = button.find_element(By.TAG_NAME, "span").text

                # Check if the button has the 'disabled' attribute
                is_available = not button.get_attribute(
                    "disabled"
                )  # True if not disabled, False if disabled

                # Store the result in the dictionary
                time_slots_availability[seating_section_title][time_slot_text] = (
                    "Available" if is_available else "Not Available"
                )

            except Exception as e:
                print(f"Error while processing a time slot: {e}")
                continue
        with open("time_slots_availability.json", "w") as json_file:
            json.dump(time_slots_availability, json_file, indent=4)


