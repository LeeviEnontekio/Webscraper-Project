from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
import csv
import random

page_url = "https://nextspaceflight.com/launches/past/?search="

driver_path = "C:\Program Files (x86)\geckodriver.exe"
s = Service(driver_path)
driver = webdriver.Firefox(service=s)
driver.get(page_url)
driver.page_source.encode("utf-8")

page_number = 0

# preparing the csv-file with headers
with open("data.csv", "w", newline="") as file:
    writer = csv.writer(file)
    header = ["Organisation", "Location", "Date", "Rocket_Status", "Price", "Mission_Status"]
    writer.writerow(header)


def search_cards():
    time.sleep(random.randint(1, 2))
    cards = driver.find_elements("css selector", ".mdc-button")
    checkup = driver.find_elements("css selector", ".mdc-button__label")
    data = {"cards": cards,
            "checkup": checkup}
    return data


def loop_cards(card_amount):
    counter = 0
    for i in range(card_amount):
        time.sleep(random.randint(1, 3))
        data = search_cards()  # refresh search the cards to not run into stale element of reference error
        if check(data["checkup"][counter]):
            data["cards"][counter].click()
            get_info()
            counter += 1
        else:
            counter += 1

    next_page()  # go to new page after looping through all the cards


def check(data):
    if data.text == "DETAILS":
        return True
    else:
        return False


def get_info():
    driver.page_source.encode("ascii", "ignore")
    time.sleep(random.randint(1, 2))

    # organisation
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("css selector", ".mdl-grid.a"))
        )
    except TimeoutException:
        print("loading the element took way too long")
        driver.quit()

    info = driver.find_elements("css selector", "div.mdl-grid.a div.mdl-cell")
    organisation = info[1].text

    # location
    location_search = driver.find_elements("css selector", "h4.mdl-card__title-text")
    for item in reversed(location_search):
        if "," in item.text:
            location = item.text
            break

    # launch time
    date = driver.find_element("css selector", "div .mdl-cell").text.split("\n")
    date = date[2]

    # rocket status
    r_status = info[2].text.replace("Status: ", "")

    # Price
    if "Price" in info[3].text:
        price = info[3].text
        price = price.split()
        price = price[1].replace("$", "")
    else:
        price = 0

    # mission status
    m_statuses = driver.find_elements("css selector", "h6.rcorners")
    for status in m_statuses:
        if "Suborbital" in status.text:
            pass
        else:
            m_status = status.text


    csv_row = [organisation, location, date, r_status, price, m_status]
    write_to_csv(csv_row)

    driver.back()  # back to main page


def write_to_csv(data_list):
    with open("data.csv", "a", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data_list)


def next_page():
    button = search_cards()
    time.sleep(random.randint(5, 10))
    for button in button["cards"]:
        try:
            if "NEXT" in button.text:
                button.click()
                break
        except:
            print("Done with scraping :)")
            driver.quit()

    global page_number
    page_number += 1
    print(f"Page number: {page_number}")
    loop_cards(get_card_amount())


def get_card_amount():
    dict = search_cards()  # finding out the amount of cards on the page
    card_amount = len(dict["cards"])
    return card_amount


loop_cards(get_card_amount())  # start looping through cards and getting info

# TODO: Make the loop faster while maintaining connection to the server
