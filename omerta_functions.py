from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from urllib.request import urlopen

import pytesseract
import numpy as np
import random
import cv2

import time
from datetime import datetime, timedelta


def create_session():
    global driver

    try:
        # open web browser and the Omerta homepage
        options = Options()
        options.add_argument("--headless") # option to have browser display or not
        options.add_argument("log-level=3") # removes excessive logging on terminal
        driver = webdriver.Chrome(executable_path= r'C:\\Users\\asusr\\Documents\\Python\\Omerta Project\\chromedriver.exe', options=options)
        driver.get("https://www.omertamafia.com/")
        time.sleep(2)
        return True
    except:
        print("Error with remote host")
        driver.quit()
        time.sleep(4)
        return False


def get_turing_key(omerta_character):
    # source the image from website
    image_url = 'https://www.omertamafia.com/turing_gen.php?character=' + omerta_character
    response = urlopen(image_url)                                   # download image
    time.sleep(2)
    img = np.asarray(bytearray(response.read()), dtype="uint8")     # convert to numpy array
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)                       # read image

    # Rescale the image
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply threshold to get image with only black & white (binarization)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # convert image to string using tesseract
    custom_config = r'--dpi 300'
    image_to_str = pytesseract.image_to_string(img, config=custom_config)
    t_key = image_to_str.strip()
    return t_key


def check_for_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def login(user_name, login_password, omerta_character):
    try:
        driver.find_element_by_name("username").send_keys(user_name)
        driver.find_element_by_name("password").send_keys(login_password)
        driver.find_element_by_css_selector("input[type='submit'][value='Login']").click()
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to login")
        return

    time.sleep(2)
    # ensures we have landed on the turning key page while trying to login
    attempt = 0

    while 1:
        xpath_message = "//table[contains(@class, 'main')]/tbody/tr/td[contains(@class, 'header_inside')]/div[2]"
        if check_for_xpath(xpath_message):
            try:
                message = driver.find_element_by_xpath(xpath_message).get_attribute("innerHTML")
            except NoSuchElementException as exception:
                print("Error handling: Element not found trying to get login message")
                return
            if message == "Session Expired":
                try:
                    driver.get("https://www.omertamafia.com/")
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to get to homepage")
                    return
                time.sleep(2)
                try:
                    driver.find_element_by_name("username").send_keys(user_name)
                    driver.find_element_by_name("password").send_keys(login_password)
                    driver.find_element_by_css_selector("input[type='submit'][value='Login']").click()
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to login")
                    return
                time.sleep(3)
            elif message == "Cheat bot check. Please enter the number:":
                break
        else:
            print("Didn't land on turing login page, trying again...")
            attempt += 1
            if attempt >= 5:
                print("Login failed, no idea why so exiting login function...")
                break

    # get passed the turing key by brute force of turing key until tesseract gets the character recognition right
    key = get_turing_key(omerta_character)
    try:
        driver.find_element_by_css_selector("[name='ivestas_kodas'][id='turing_static']").send_keys(key)
        driver.find_element_by_css_selector("input[type='submit'][class='submit']").click()
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get past turing key")
        return

    while 1:
        # if td class="header_inside" (main part of game) contains class="success" 'Correct ' we are in!
        if check_for_xpath("//div[contains(@class, 'success') and text()='Correct ']"):
            print(f"Successfully logged in as {omerta_character} @ {datetime.now().hour}:{datetime.now().minute}")
            break
        elif check_for_xpath("//div[contains(@class, 'error') and text()='Incorrect number']"):
            print("Key didn't work, trying again...")
            time.sleep(3)
            key = get_turing_key(omerta_character)
            try:
                driver.find_element_by_css_selector(
                    "input[type='text'][name='ivestas_kodas'][id='turing_static']").send_keys(key)
                driver.find_element_by_css_selector("input[type='submit'][class='submit']").click()
            except NoSuchElementException as exception:
                print("Error handling: Element not found trying to submit turing key")
                return
        else:
            print("Not sure what is going on")
            return


def logout():
    # logout, close browser and exit script
    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=logout")
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to login")
        return
    time.sleep(4)
    print(f"Logged out @ {datetime.now().hour}:{datetime.now().minute}")
    driver.quit()


def get_rank_level():
    try:
        xpath_rank_level = ("//table[contains(@class, 'main')]/tbody/tr\
                             /td[contains(@class, 'header_inside')]/div[contains(@class, 'inside_top')]\
                             /div[contains(@class, 'inside_top_row_4')]\
                             /div[contains(@class, 'inside_top_row_4_4')]/img[2]")
        rank_level = int(driver.find_element_by_xpath(xpath_rank_level).get_attribute("alt"))
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get rank level")
        return
    return rank_level


def get_rank():
    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=status")
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get to status page")
        return
    time.sleep(2)
    xpath_rank = ("//table[contains(@class, 'main')]/tbody/tr\
                   /td[contains(@class, 'header_inside')]\
                   /div[3]/table/tbody/tr[7]/td[2]")
    try:
        f_rank = driver.find_element_by_xpath(xpath_rank).get_attribute("innerHTML")
        return f_rank
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get rank")
        return


def get_illegal_cash():
    try:
        xpath_illegal_cash = ("//table[contains(@class, 'main')]/tbody/tr\
        /td[contains(@class, 'header_inside')]\
        /div[contains(@class, 'inside_top')]\
        /div[contains(@class, 'inside_top_row_4')]\
        /div[contains(@class, 'inside_top_row_4_1')]\
        /strong[2]")
        illegal_cash = int(driver.find_element_by_xpath(xpath_illegal_cash).get_attribute("innerHTML")[:-1])
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get illegal cash")
        return
    return illegal_cash


def get_ks():
    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=status")
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get to status page")
        return
    time.sleep(2)
    xpath_ks = ("//table[contains(@class, 'main')]/tbody/tr\
                     /td[contains(@class, 'header_inside')]\
                     /div[3]/table/tbody/tr[14]/td[2]/img")
    try:
        f_ks = driver.find_element_by_xpath(xpath_ks).get_attribute("alt")
        return f_ks
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get ks")
        return


def get_action_points():
    try:
        xpath_action_points = ("//table[contains(@class, 'main')]/tbody/tr\
        /td[contains(@class, 'header_inside')]\
        /div[contains(@class, 'inside_top')]\
        /div[contains(@class, 'inside_top_row_4')]\
        /div[contains(@class, 'inside_top_row_4_3')]\
        /strong[2]/span[contains(@id, 'AP')]")
        action_points = int(driver.find_element_by_xpath(xpath_action_points).get_attribute("innerHTML"))
    except NoSuchElementException as exception:
        try:
            driver.get("https://www.omertamafia.com/index2.php?bir=status")
            xpath_action_points = ("//table[contains(@class, 'main')]/tbody/tr\
            /td[contains(@class, 'header_inside')]\
            /div[contains(@class, 'inside_top')]\
            /div[contains(@class, 'inside_top_row_4')]\
            /div[contains(@class, 'inside_top_row_4_3')]\
            /strong[2]/span[contains(@id, 'AP')]")
            action_points = int(driver.find_element_by_xpath(xpath_action_points).get_attribute("innerHTML"))
        except NoSuchElementException as exception:
            print("Error handling: Element not found trying to get action points")
            return
    return action_points


def get_suspicion_level():
    try:
        xpath_suspicion_level = ("//table[contains(@class, 'main')]/tbody/tr\
                                  /td[contains(@class, 'header_inside')]/div[contains(@class, 'inside_top')]\
                                  /div[contains(@class, 'inside_top_row_4')]\
                                  /div[contains(@class, 'inside_top_row_4_4')]/img[1]")
        suspicion_level = int(driver.find_element_by_xpath(xpath_suspicion_level).get_attribute("alt"))
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get suspicion level")
        return
    return suspicion_level


def bribe_officials():
    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=bribe")
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get to bribe page")
        return
    time.sleep(2)

    suspicion_level = get_suspicion_level()
    illegal_cash = get_illegal_cash()

    try:
        xpath_bribe_price = ("//table[contains(@class, 'main')]/tbody/tr\
                              /td[contains(@class, 'header_inside')]\
                              /table/tbody/tr/td/form/table/tbody/tr/td[2]")

        bribe_price = int(driver.find_element_by_xpath(xpath_bribe_price).get_attribute("innerHTML")[1:-6])
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get bribe price")
        return
    try:
        while suspicion_level >= 10:
            illegal_cash = get_illegal_cash()
            if suspicion_level >= 10 and illegal_cash > bribe_price:
                try:
                    driver.find_element_by_css_selector("input[type='radio'][value='1']").click()
                    driver.find_element_by_css_selector("input[type='radio'][value='1']").send_keys(Keys.RETURN)
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to bribe officials")
                    return
                time.sleep(1)
                try:
                    driver.get("https://www.omertamafia.com/index2.php?bir=bribe")
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to get to bribe page")
                    return
                suspicion_level = get_suspicion_level()
                print(f"Officials have been bribed and suspicion level is now: {suspicion_level}")
            elif illegal_cash < bribe_price:
                print("You can't afford to bribe officials")
                break
            else:
                print("Unable to bribe officials...")
                break
    except:
        print("Error handling: If statement break")
        return


def rank_up():  # potential enhancement - send ap to spend on ranking up
    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=theft")
        action_points = get_action_points()
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get theft page")
        return
    try:
        while action_points >= 10:
            try:
                driver.find_element_by_css_selector("input[type='text'][name='hustle']").send_keys("10")
                driver.find_element_by_css_selector("input[type='text'][name='hustle']").send_keys(Keys.RETURN)
            except NoSuchElementException as exception:
                print("Error handling: Element not found trying to hustle")
                return
            time.sleep(1)
            action_points = get_action_points()
        print("Finished hustling")
        bribe_officials()
    except:
        print("Error handling: If statement break")
        return


def get_info(character):
    rank = get_rank()
    cash = get_illegal_cash()
    ks = get_ks()
    rank_progress = get_rank_level()
    info_request = (character, rank, cash, ks, rank_progress)
    return info_request


def garage_work():
    action_points = get_action_points()
    illegal_cash = get_illegal_cash()

    print("Started garage work")
    # default xpath_dismantle value assumes table count is two
    xpath_dismantle = ("//table[contains(@class, 'main')]/tbody/tr\
                        /td[contains(@class, 'header_inside')]\
                        /table[2]/tbody/tr[2]/td[6]/a")

    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=garage")
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get to garage page")
        return
    time.sleep(2)

    while 1:
        try:
            driver.get("https://www.omertamafia.com/index2.php?bir=garage")
            time.sleep(2)
        except NoSuchElementException as exception:
            print("Error handling: Element not found trying to quickly refresh the garage page")
            return

        # determine if there are dismantles and or offers
        try:
            xpath_table_count = ("//table[contains(@class, 'main')]/tbody/tr\
                                  /td[contains(@class, 'header_inside')]/table")
            table_count = len(driver.find_elements_by_xpath(xpath_table_count))
        except NoSuchElementException as exception:
            print("Error handling: Element not found trying to get table count")
            return

        if table_count >= 4:
            print("You have not yet maxed out the garage so code won't work")
        elif table_count == 3:
            # you have dismantles and offers
            # determine how many dismantles
            xpath_dismantle_count = ("//table[contains(@class, 'main')]/tbody/tr\
                                      /td[contains(@class, 'header_inside')]\
                                      /table[3]/tbody/tr")
            xpath_dismantle = ("//table[contains(@class, 'main')]/tbody/tr\
                                /td[contains(@class, 'header_inside')]\
                                /table[3]/tbody/tr[2]/td[6]/a")
            try:
                cars_to_dismantle = len(driver.find_elements_by_xpath(xpath_dismantle_count))
                # print(f"You have {cars_to_dismantle - 1} cars to dismantle")
            except NoSuchElementException as exception:
                print("Error handling: Element not found trying to get dismantle count")
                return

            # determine how many offers
            xpath_offer_count = ("//table[contains(@class, 'main')]/tbody/tr\
                                  /td[contains(@class, 'header_inside')]\
                                  /table[2]/tbody/tr")
            try:
                offer_count = len(driver.find_elements_by_xpath(xpath_offer_count))
                # print(f"Car offer count is {offer_count - 1}")
            except NoSuchElementException as exception:
                print("Error handling: Element not found trying to get car offer count")
                return

        elif table_count == 2:
            # you have either dismantles or offers
            xpath_table_id = ("//table[contains(@class, 'main')]/tbody/tr\
                               /td[contains(@class, 'header_inside')]\
                               /table[2]/tbody/tr[1]/td[6]")
            try:
                table_id = driver.find_element_by_xpath(xpath_table_id).get_attribute("innerHTML")
            except NoSuchElementException as exception:
                print("Error handling: Element not found trying to get table id")
                return

            cars_to_dismantle = 0
            offer_count = 0

            if table_id == "Dismantle":
                # determine how many dismantles
                xpath_dismantle_count = ("//table[contains(@class, 'main')]/tbody/tr\
                                          /td[contains(@class, 'header_inside')]\
                                          /table[2]/tbody/tr")
                xpath_dismantle = ("//table[contains(@class, 'main')]/tbody/tr\
                                    /td[contains(@class, 'header_inside')]\
                                    /table[2]/tbody/tr[2]/td[6]/a")
                try:
                    cars_to_dismantle = len(driver.find_elements_by_xpath(xpath_dismantle_count))
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to get dismantle count")
                    return
            else:
                # determine how many offers
                xpath_offer_count = ("//table[contains(@class, 'main')]/tbody/tr\
                                      /td[contains(@class, 'header_inside')]\
                                      /table[2]/tbody/tr")
                try:
                    offer_count = len(driver.find_elements_by_xpath(xpath_offer_count))
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to get car offer count")
                    return

        elif table_count == 1:
            print("Table count is ONE, must mean garage is empty")
            print("Exiting garage")
            break

        elif table_count == 0:
            print("You don't have a garage so why are you trying to chop?")
            print("Exiting garage")
            break

        else:
            print("Something went wrong with the table count, exiting garage")
            break

        # once you know what the workshop looks like, dismantle while action points > 4
        try:
            if cars_to_dismantle > 1 and action_points > 24:
                try:
                    driver.find_element_by_xpath(xpath_dismantle).click()
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to dismantle car")
                    return
                time.sleep(1)
                action_points = get_action_points()

            # then proceed to accept offers while money > 50k and if offers meet criteria
            elif offer_count > 1 and illegal_cash > 50000:
                xpath_offer_details = ("//table[contains(@class, 'main')]/tbody/tr\
                                        /td[contains(@class, 'header_inside')]\
                                        /table[2]/tbody/tr[2]/td")
                xpath_offer_accept = ("//table[contains(@class, 'main')]/tbody/tr\
                                       /td[contains(@class, 'header_inside')]\
                                       /table[2]/tbody/tr[2]/td[6]/a")
                xpath_offer_reject = ("//table[contains(@class, 'main')]/tbody/tr\
                                       /td[contains(@class, 'header_inside')]\
                                       /table[2]/tbody/tr[2]/td[7]/a")
                try:
                    offer_details = driver.find_elements_by_xpath(xpath_offer_details)
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to get offer details")
                    return

                offer_details_data = []

                for detail in offer_details:
                    offer_details_data.append(detail.text)

                offer_car_level = int(offer_details_data[1])
                offer_cash_for_car = int(offer_details_data[2][:-2])

                acceptable_offers = {
                    1: 8000,           # usually 8000 but not currently accepting this level of car
                    2: 10000,          # usually 10000 but not currently accepting this level of car
                    3: 13000,          # usually 13000 but not currently accepting this level of car
                    4: 16000,          # usually 16000
                    5: 21000           # usually 21000
                }

                if offer_cash_for_car <= acceptable_offers[offer_car_level]:
                    # print("Accepting offer")
                    try:
                        driver.find_element_by_xpath(xpath_offer_accept).click()
                    except NoSuchElementException as exception:
                        print("Error handling: Element not found trying to accept car offer")
                        return
                    illegal_cash = get_illegal_cash()
                else:
                    print("Offer rejected")
                    try:
                        driver.find_element_by_xpath(xpath_offer_reject).click()
                    except NoSuchElementException as exception:
                        print("Error handling: Element not found trying to reject offer")
                        return

            else:
                print("Work in garage complete")
                break
        except:
            print("Error handling: If statement break")
            return
    
    print(f"You have {cars_to_dismantle} cars to dismantle and {offer_count} car offers")


def steal_cars(count=12):
    action_points = get_action_points()
    illegal_cash = get_illegal_cash()
    f_rank = get_rank()

    rank_to_security_level = {
        "Newbie": 1,
        "Gangster": 2,
        "Wiseguy": 3,
        "Made Man": 4,
        "Capo": 5,
        "Boss": 5,
        "Godfather": 5
    }

    print("Started stealing cars")

    xpath_message = "//table[contains(@class, 'main')]/tbody/tr/td[contains(@class, 'header_inside')]/div[2]"

    target_car = ""
    s_count = 0

    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=ath")
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get to auto theft page")
        return
    time.sleep(2)

    try:
        while action_points > 4 and illegal_cash > 50000 and s_count < count:
            try:
                driver.get("https://www.omertamafia.com/index2.php?bir=ath")
            except NoSuchElementException as exception:
                print("Error handling: Element not found trying to quickly refresh auto theft page")
                return

            # if target_car is an empty string then get url to click
            if not bool(target_car):
                xpath_auto_parked = ("//table[contains(@class, 'main')]/tbody/tr\
                                      /td[contains(@class, 'header_inside')]\
                                      /table[1]/tbody/tr[3]/td")
                try:
                    auto_parked = driver.find_elements_by_xpath(xpath_auto_parked)
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to get autos parked")
                    return

                auto_details_data = []

                for auto in auto_parked:
                    auto_details_data.append(auto.text)

                auto_security_level = int(auto_details_data[3])

                if auto_security_level == rank_to_security_level[f_rank]:
                    xpath_steal_auto = ("//table[contains(@class, 'main')]/tbody/tr\
                                         /td[contains(@class, 'header_inside')]\
                                         /table[1]/tbody/tr[3]/td[5]/a")
                    try:
                        target_car = driver.find_element_by_xpath(xpath_steal_auto).get_attribute("href")
                    except NoSuchElementException as exception:
                        print("Error handling: Element not found trying to find target car")
                        return

            elif bool(target_car):
                try:
                    driver.get(target_car)
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to get target car")
                    return
                time.sleep(1)

            if check_for_xpath(xpath_message):
                try:
                    message = driver.find_element_by_xpath(xpath_message).get_attribute("innerHTML")
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to get auto message")
                    return
                # print(message)
                if message == "You need at least screwdriver to steal a car":
                    # determine the tool location
                    xpath_table_count = ("//table[contains(@class, 'main')]/tbody/tr\
                                          /td[contains(@class, 'header_inside')]/table")
                    try:
                        table_id = len(driver.find_elements_by_xpath(xpath_table_count))
                    except NoSuchElementException as exception:
                        print("Error handling: Element not found trying to get table count")
                        return

                    xpath_buy_tool = ("//table[contains(@class, 'main')]/tbody/tr\
                                       /td[contains(@class, 'header_inside')]\
                                       /table[" + str(table_id) + "]/tbody\
                                       /tr[" + str(rank_to_security_level[f_rank]) + "]/td[2]\
                                       /form/input[contains(@class, 'submit')]")
                    try:
                        driver.find_element_by_xpath(xpath_buy_tool).click()
                    except NoSuchElementException as exception:
                        print("Error handling: Element not found trying to buy tools")
                        return
                    time.sleep(1)
                elif message == "The car was successfully stolen":
                    action_points = get_action_points()
                    illegal_cash = get_illegal_cash()
                    s_count += 1
                    continue
                elif message == "Car's alarm worked well and police caught you":
                    action_points = get_action_points()
                    illegal_cash = get_illegal_cash()
                    continue
                elif message == "You haven't got enough action points":
                    action_points = get_action_points()
                    illegal_cash = get_illegal_cash()
                    continue
                else:
                    try:
                        driver.find_element_by_xpath(xpath_buy_tool).click()
                        print("New tool bought to match rank!") # change in rank doesn't work as this needs done sooner in code or just loops round
                    except NoSuchElementException as exception:
                        print("Error handling: Element not found trying to buy tool as no longer matches rank")
                        return
                    break

            action_points = get_action_points()
            illegal_cash = get_illegal_cash()

        # once finished stealing cars (ap = 0) then bribe officials if you need to
        bribe_officials()
    except:
        print("Error handling: If statement break")
        return


def offer_cars(chop_shop="Moleone", car_count=0, car_level=0):
    # get rank
    f_rank = get_rank()

    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=ath")
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get to auto theft page")
        return
    time.sleep(2)

    offer_price = {
        1: 5000,
        2: 6000,
        3: 12000,
        4: 16000,
        5: 20000
    }

    # default is to offer all cars to the John chop shop at a discounted price, based on character rank
    if chop_shop == "John" and car_count == 0 and car_level == 0:
        offer_price = {
            "Newbie": 2500,
            "Gangster": 3000,
            "Wiseguy": 6000,
            "Made Man": 8000,
            "Capo": 10000,
            "Boss": 10000,
            "Godfather": 10000
        }

        xpath_chop_shop = ("//table[contains(@class, 'main')]/tbody/tr\
                            /td[contains(@class, 'header_inside')]\
                            /table[2]/tbody/tr[2]/td/form/select/option[contains(@value, '" + chop_shop + "')]")

        try:
            driver.find_element_by_css_selector("input[type='text'][name='prize2']").send_keys(offer_price[f_rank])
            driver.find_element_by_xpath(xpath_chop_shop).click()
            driver.find_element_by_css_selector("input[type='submit'][value='OK']").click()
        except NoSuchElementException as exception:
            print("Error handling: Element not found trying to offer car")
            return
        print(f"Cars sent to {chop_shop}")

    # if only the chop_shop is specified send all cars here at a price based on character rank
    elif car_count == 0 and car_level == 0:
        offer_price = {
            "Newbie": 5000,
            "Gangster": 6000,
            "Wiseguy": 12000,
            "Made Man": 16000,
            "Capo": 20000,
            "Boss": 20000,
            "Godfather": 20000
        }

        xpath_chop_shop = ("//table[contains(@class, 'main')]/tbody/tr\
                            /td[contains(@class, 'header_inside')]\
                            /table[2]/tbody/tr[2]/td/form/select/option[contains(@value, '" + chop_shop + "')]")

        try:
            driver.find_element_by_css_selector("input[type='text'][name='prize2']").send_keys(offer_price[f_rank])
            driver.find_element_by_xpath(xpath_chop_shop).click()
            driver.find_element_by_css_selector("input[type='submit'][value='OK']").click()
        except NoSuchElementException as exception:
            print("Error handling: Element not found trying to offer car")
            return
        print(f"Cars offered to {chop_shop}")

    # if chop_shop and car_count are specified then send the top x cars to the specified chop shop
    elif car_count != 0 and car_level == 0:
        xpath_total_car_count = ("//table[contains(@class, 'main')]/tbody/tr\
                                            /td[contains(@class, 'header_inside')]\
                                            /table[2]/tbody/tr")
        try:
            total_car_count = len(driver.find_elements_by_xpath(xpath_total_car_count)) - 3
        except NoSuchElementException as exception:
            print("Error handling: Element not found trying to get car count")
            return

        car_count_tally = 0

        for car in range(4, total_car_count + 4):
            if car_count_tally < car_count:
                xpath_offer_car_level = ("//table[contains(@class, 'main')]/tbody/tr\
                                             /td[contains(@class, 'header_inside')]\
                                             /table[2]/tbody/tr[" + str(car) + "]/td[4]")
                try:
                    ocl = int(driver.find_element_by_xpath(xpath_offer_car_level).get_attribute("innerHTML"))
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to get offer car level")
                    return

                xpath_offer_price = ("//table[contains(@class, 'main')]/tbody/tr\
                                            /td[contains(@class, 'header_inside')]\
                                            /table[2]/tbody/tr[" + str(car) + "]/td[5]\
                                            /input[contains(@type, 'text')]")

                xpath_chop_shop = ("//table[contains(@class, 'main')]/tbody/tr\
                                                            /td[contains(@class, 'header_inside')]\
                                                            /table[2]/tbody/tr[" + str(car) + "]/td[6]\
                                                            /select/option[contains(@value, '" + chop_shop + "')]")
                if check_for_xpath(xpath_chop_shop):
                    try:
                        driver.find_element_by_xpath(xpath_offer_price).send_keys(offer_price[ocl])
                        driver.find_element_by_xpath(xpath_chop_shop).click()
                    except NoSuchElementException as exception:
                        print("Error handling: Element not found trying to get offer price")
                        return
                    car_count_tally += 1
                    time.sleep(2)
                else:
                    continue

        print(f"Sent {car_count_tally} cars to {chop_shop}")

    # if both car_count and car_level have been specified then offer chop_shop x amount of level x cars
    else:
        xpath_total_car_count = ("//table[contains(@class, 'main')]/tbody/tr\
                                    /td[contains(@class, 'header_inside')]\
                                    /table[2]/tbody/tr")

        try:
            total_car_count = len(driver.find_elements_by_xpath(xpath_total_car_count)) - 3
        except NoSuchElementException as exception:
            print("Error handling: Element not found trying to get total car count")
            return

        car_count_tally = 0

        for car in range(4, total_car_count + 4):
            if car_count_tally < car_count:
                xpath_offer_car_level = ("//table[contains(@class, 'main')]/tbody/tr\
                                     /td[contains(@class, 'header_inside')]\
                                     /table[2]/tbody/tr[" + str(car) + "]/td[4]")
                try:
                    ocl = int(driver.find_element_by_xpath(xpath_offer_car_level).get_attribute("innerHTML"))
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to get offer car level")
                    return

                if ocl == car_level:
                    xpath_offer_price = ("//table[contains(@class, 'main')]/tbody/tr\
                                        /td[contains(@class, 'header_inside')]\
                                        /table[2]/tbody/tr[" + str(car) + "]/td[5]\
                                        /input[contains(@type, 'text')]")

                    xpath_chop_shop = ("//table[contains(@class, 'main')]/tbody/tr\
                                                        /td[contains(@class, 'header_inside')]\
                                                        /table[2]/tbody/tr[" + str(car) + "]/td[6]\
                                                        /select/option[contains(@value, '" + chop_shop + "')]")
                    if check_for_xpath(xpath_chop_shop):
                        try:
                            driver.find_element_by_xpath(xpath_offer_price).send_keys(offer_price[ocl])
                            driver.find_element_by_xpath(xpath_chop_shop).click()
                        except NoSuchElementException as exception:
                            print("Error handling: Element not found trying to get offer price")
                            return
                        car_count_tally += 1
                        time.sleep(2)
                    else:
                        continue

        print(f"Sent {car_count_tally} level {car_level} cars to {chop_shop}")


def whack_a_fool():
    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=war")
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get to war page")
        return
    time.sleep(4)

    action_points = get_action_points()
    illegal_cash = get_illegal_cash()

    kill_list = [
        "LaGuapita"
    ]

    shots = 0

    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=war")
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get to war page")
        return
    time.sleep(2)

    for victim in kill_list:
        try:
            if action_points >= 20 and illegal_cash >= 20000:
                try:
                    driver.find_element_by_css_selector("input[type='radio'][value='1']").click()
                    driver.find_element_by_name("dude").send_keys(victim)
                    driver.find_element_by_name("dude").send_keys(Keys.RETURN)
                except NoSuchElementException as exception:
                    print(f"Error handling: Element not found trying to whack {victim}")
                    return
                time.sleep(2)
                try:
                    driver.switch_to.alert.accept()
                except NoSuchElementException as exception:
                    print(f"Error handling: Element not found trying to whack {victim} alert button")
                    return
                print(f"You shot at {victim}")
                shots += 1
                action_points = get_action_points()
                illegal_cash = get_illegal_cash()
                time.sleep(2)

                # add post in forum code here
                xpath_message = ("//table[contains(@class, 'main')]/tbody/tr\
                                 /td[contains(@class, 'header_inside')]/div[3]")
                if check_for_xpath(xpath_message):
                    try:
                        message = driver.find_element_by_xpath(xpath_message).get_attribute("innerHTML")
                    except NoSuchElementException as exception:
                        print(f"Error handling: Element not found trying to find message")
                        return
                    print(message)
                    time.sleep(31)
                #
                #     # posts failed attempt in family forum
                #     if message == "Attempt failed":
                #         # go to forum and post
                #         try:
                #             driver.get("https://www.omertamafia.com/index2.php?bir=thread&th=280&forid=2687")
                #         except NoSuchElementException as exception:
                #             print(f"Error handling: Element not found trying to get to forum page")
                #             return
                #         time.sleep(2)
                #
                #         xpath_forum_message = ("//table[contains(@class, 'main')]/tbody/tr\
                #                                /td[contains(@class, 'header_inside')]\
                #                                /table[1]/tbody/tr[2]/td/div/form/table/tbody/tr[1]/td/textarea")
                #
                #         xpath_forum_ok_button = ("//table[contains(@class, 'main')]/tbody/tr\
                #                                  /td[contains(@class, 'header_inside')]\
                #                                  /table[1]/tbody/tr[2]/td/div/form/table/tbody/tr[2]/td/input")
                #
                #         try:
                #             driver.find_element_by_xpath(xpath_forum_message).send_keys(victim)
                #             driver.find_element_by_xpath(xpath_forum_ok_button).click()
                #         except NoSuchElementException as exception:
                #             print(f"Error handling: Element not found trying to post message")
                #             return
                #         time.sleep(2)
                #
                #         try:
                #             driver.get("https://www.omertamafia.com/index2.php?bir=war")
                #         except NoSuchElementException as exception:
                #             print("Error handling: Element not found trying to get back to war page")
                #             return
                #         time.sleep(2)
                #     else:
                #         continue

                try:
                    driver.find_element_by_css_selector("input[type='radio'][value='3']").click()
                    driver.find_element_by_name("dude").send_keys(victim)
                    driver.find_element_by_name("dude").send_keys(Keys.RETURN)
                except NoSuchElementException as exception:
                    print(f"Error handling: Element not found trying to beat {victim}")
                    return
                time.sleep(2)
                try:
                    driver.switch_to.alert.accept()
                except NoSuchElementException as exception:
                    print(f"Error handling: Element not found trying to beat {victim} alert button")
                    return
                print(f"You tried to beat {victim}")
            else:
                break
        except:
            print("Error handling: If statement break")
            return

    # print(f"Shot count is at {shots}")
    bribe_officials()


shots_taken=[] # global var for tracking shots taken


def reset_ks_list():
    global shots_taken
    shots_taken = []
    print(f"Shots taken list reset: {shots_taken}")


def shoot_for_ks():
    action_points = get_action_points()
    illegal_cash = get_illegal_cash()
    f_rank = get_rank()

    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=hitlist&hitlist_type=1")
        time.sleep(2)
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get to hitlist page")
        return

    # capture all available hitlist data
    xpath_hitlist_count = ("//table[contains(@class, 'main')]/tbody/tr\
                            /td[contains(@class, 'header_inside')]\
                            /table/tbody/tr")
    try:
        hitlist_count = len(driver.find_elements_by_xpath(xpath_hitlist_count))
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get hitlist count")
        return
    print("Started shooting for ks")

    hitlist_details = []

    for hit in range(1, hitlist_count + 1):
        xpath_target_detail_count = ("//table[contains(@class, 'main')]/tbody/tr\
                                      /td[contains(@class, 'header_inside')]\
                                      /table/tbody/tr[" + str(hit) + "]/td")
        try:
            target_detail_count = len(driver.find_elements_by_xpath(xpath_target_detail_count))
        except NoSuchElementException as exception:
            print("Error handling: Element not found trying to get target detail count")
            return

        target_detail_summary = []

        for detail in range(1, target_detail_count + 1):
            if detail == 4:
                xpath_target_detail = ("//table[contains(@class, 'main')]/tbody/tr\
                                        /td[contains(@class, 'header_inside')]\
                                        /table/tbody/tr[" + str(hit) + "]/td[" + str(detail) + "]/a")
                try:
                    target_detail = driver.find_element_by_xpath(xpath_target_detail).get_attribute("href")
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to target details")
                    return
            else:
                xpath_target_detail = ("//table[contains(@class, 'main')]/tbody/tr\
                                        /td[contains(@class, 'header_inside')]\
                                        /table/tbody/tr[" + str(hit) + "]/td[" + str(detail) + "]")
                try:
                    target_detail = driver.find_element_by_xpath(xpath_target_detail).get_attribute("innerHTML")
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to target details")
                    return

            target_detail_summary.append(target_detail)

        hitlist_details.append(tuple(target_detail_summary))

    # refine hitlist targets based on character rank
    rank_structure = {
        "Newbie": 1,
        "Gangster": 2,
        "Wiseguy": 3,
        "Made Man": 4,
        "Capo": 5,
        "Boss": 6,
        "Godfather": 7
    }
    
    hitlist_targets_at_rank = []
    hitlist_targets_below_rank = []
    hitlist_targets_two_below_rank = []

    for hit_index, hit_rank, hit_name, hit_url in hitlist_details:
        if hit_name in shots_taken:
            continue
        else:
            if rank_structure[hit_rank] == rank_structure[f_rank]:
                hitlist_targets_at_rank.append((hit_name, hit_rank, hit_url))
            elif rank_structure[hit_rank] == (rank_structure[f_rank] - 1):
                hitlist_targets_below_rank.append((hit_name, hit_rank, hit_url))
            elif rank_structure[hit_rank] == (rank_structure[f_rank] - 2):
                hitlist_targets_two_below_rank.append((hit_name, hit_rank, hit_url))

    random.shuffle(hitlist_targets_two_below_rank)
    random.shuffle(hitlist_targets_below_rank)
    random.shuffle(hitlist_targets_at_rank)

    hitlist = hitlist_targets_two_below_rank + hitlist_targets_below_rank + hitlist_targets_at_rank

    if len(hitlist) == 0:
        print("There doesn't appear to be anyone to shoot at for ks...")
        return

    # shot at targets
    for target_name, target_rank, target_url in hitlist:
        try:
            if action_points >= 20 and illegal_cash >= 40000:
                try:
                    driver.get(target_url)
                    time.sleep(2)
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to shoot at target")
                    return
                # print(f"-- Shot at {target_name} who is a {target_rank}")

                xpath_message = ("//table[contains(@class, 'main')]/tbody/tr\
                                  /td[contains(@class, 'header_inside')]/div[3]")
                if check_for_xpath(xpath_message):
                    try:
                        message = driver.find_element_by_xpath(xpath_message).get_attribute("innerHTML")
                    except NoSuchElementException as exception:
                        print("Error handling: Element not found trying to get hit message")
                        return

                    if message == 'Your target has recently survived whack attempt':
                        shots_taken.append(target_name)
                    elif message == 'Attempt failed':
                        shots_taken.append(target_name)
                        print(f"Shooting: {message}")
                    elif message == 'Your target is already dead':
                        shots_taken.append(target_name)
                    elif message == '<span id="countdown_kill">(09 s)</span>':
                        print(f'*** YOU HAVE KILLED {target_name.upper()} ***')
                        shots_taken.append(target_name)
                    elif message == '<span id="countdown_kill">(08 s)</span>':
                        print(f'*** YOU HAVE KILLED {target_name.upper()} ***')
                        shots_taken.append(target_name)
                    elif message == "You have reached maximum killing skill working on worldwide contracts":
                        print("MAX KS REACHED!!! AWESOME, NOW CHANGE FOCUS OF CHARACTER")
                        break
                    elif message == "You haven't got enough action points":
                        break
                    else:
                        print(message)
                time.sleep(12)
            elif illegal_cash <= 20000:
                print("You need cash to shoot")
                break
            elif action_points < 20:
                print("Out of AP")
                break
        except:
            print("Error handling: If statement break")
            return

        action_points = get_action_points()
        illegal_cash = get_illegal_cash()

    bribe_officials()


def get_cash(withdrawal=100000):
    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=bank")
        time.sleep(2)
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get to bank page")
        return
    try:
        driver.find_element_by_css_selector("input[type='text'][name='suma2']").send_keys(withdrawal)
        driver.find_element_by_css_selector("input[type='text'][name='suma2']").send_keys(Keys.RETURN)
        time.sleep(2)
        print(f"You have withdrawn ${withdrawal} from the bank")
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to withdraw cash")
        return


def rank_up_with_cfm(total_price, price_per_100):  # potential enhancement - send ap to spend on ranking up
# go to theft page
    try:
        driver.get("https://www.omertamafia.com/index2.php?bir=theft")
        action_points = get_action_points()
        illegal_cash = get_illegal_cash()
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get theft page")
        return

# find out how much CFM character has
    xpath_cfm_str = ("//table[contains(@class, 'main')]/tbody/tr\
                      /td[contains(@class, 'header_inside')]\
                      /table/tbody/tr[4]/td/form/table/tbody/tr[1]/td")

    try:
        cfm_str = driver.find_element_by_xpath(xpath_cfm_str).get_attribute("innerHTML")
    except NoSuchElementException as exception:
        print("Error handling: Element not found trying to get cfm string")
        return

    try:
        cfm = [int(s) for s in cfm_str.split() if s.isdigit()]
    except:
        print("Error handling: cfm value issue caused function to return")
        return

    try:
        while action_points >= 10:
            if cfm[0] > 0:
                try:
                    driver.find_element_by_css_selector("input[type='text'][name='launder']").send_keys("10")
                    driver.find_element_by_css_selector("input[type='text'][name='launder']").send_keys(Keys.RETURN)
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to launder")
                    return
                time.sleep(2)
                action_points = get_action_points()

            elif cfm[0] == 0 and illegal_cash > total_price:
                # go to CFM page
                try:
                    driver.get("https://www.omertamafia.com/index2.php?bir=countermarket")
                except NoSuchElementException as exception:
                    print("Error handling: Element not found trying to get cfm page")
                    return

                # find out top offer details
                xpath_total_oprice = ("//table[contains(@class, 'main')]/tbody/tr\
                                       /td[contains(@class, 'header_inside')]\
                                       /table/tbody/tr[3]/td/table/tbody/tr[2]/td[3]")

                xpath_oprice_per_100 = ("//table[contains(@class, 'main')]/tbody/tr\
                                         /td[contains(@class, 'header_inside')]\
                                         /table/tbody/tr[3]/td/table/tbody/tr[2]/td[4]")

                xpath_ocfm_link = ("//table[contains(@class, 'main')]/tbody/tr\
                                    /td[contains(@class, 'header_inside')]\
                                    /table/tbody/tr[3]/td/table/tbody/tr[2]/td[5]/a")

                total_oprice = driver.find_element_by_xpath(xpath_total_oprice).get_attribute("innerHTML")
                total_oprice = int(total_oprice.strip()[1:])

                oprice_per_100 = driver.find_element_by_xpath(xpath_oprice_per_100).get_attribute("innerHTML")
                oprice_per_100 = int(oprice_per_100.strip())

                ocfm_link = driver.find_element_by_xpath(xpath_ocfm_link).get_attribute("href")

                # if total_price and price_per_100 meet(less than) function parameters then buy
                if total_oprice <= total_price and oprice_per_100 <= price_per_100:
                    driver.get(ocfm_link)
                    print(f"Purchased ${total_oprice} of CFM")
                    time.sleep(2)
                    driver.get("https://www.omertamafia.com/index2.php?bir=theft")
                    time.sleep(2)
                    xpath_cfm_str = ("//table[contains(@class, 'main')]/tbody/tr\
                                      /td[contains(@class, 'header_inside')]\
                                      /table/tbody/tr[4]/td/form/table/tbody/tr[1]/td")

                    cfm_str = driver.find_element_by_xpath(xpath_cfm_str).get_attribute("innerHTML")
                    cfm = [int(s) for s in cfm_str.split() if s.isdigit()]
                else:
                    print("No CFM available at the offer price and price per $100 as specified")
                    return

            else:
                print("Error with CFM function, possibly no cash. Breaking while loop")
                print(f"Cash: {illegal_cash}")

                break

        print("Finished laundering")
        bribe_officials()
    except:
        print("Error handling: If statement for laundering break")
        return


