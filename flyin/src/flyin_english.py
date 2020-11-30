import re

from appium import webdriver
from datetime import date, datetime
from time import sleep
from appium.webdriver.common.touch_action import TouchAction
from flyin.src.utils import Utils
import unicodedata
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType
import json
import logging
from flyin.src import flyin_calender as cal
from flyin.src import googlesheet as gs
import pandas as pd


def convert_string_to_list_of_tuples(days):
    no_of_days = []
    temp = []
    for token in days.split(","):
        num = int(token.replace("(", "").replace(")", ""))
        temp.append(num)
        if ")" in token:
            no_of_days.append(tuple(temp))
            temp = []
    return no_of_days


class Flyinflights:
    def __init__(self):
        self.apk_path = '/Users/mitesh.gala/MobileApps/Android/Flyin.apk'
        self.platformName = 'Android'
        self.devicename = 'Android Nexus 5'
        self.platformVersion = '11.0'
        self.noReset = True
        self.driver = None
        self.checkin_date = None
        self.checkout_date = None
        self.findElementsWaitTimeout = 30
        self.appwaitactivity = "com.flyin.bookings.activities.SplashScreenActivity"
        self.appPackage = "com.flyin.bookings"

    def long_sleep(self):
        sleep(5)

    def short_sleep(self):
        sleep(3)

    def createDesiredCapabilty(self):
        desired_capabilties = {
            "platformName": self.platformName,
            "platformVersion": self.platformVersion,
            "deviceName": self.devicename,
            "app": self.apk_path,
            "appPackage": self.appPackage,
            "appActivity": self.appwaitactivity,
            "noReset": self.noReset,
            "clearSystemFiles": True
        }
        return desired_capabilties

    def waitForElementPopUp(self, element: str, find_type: str):
        if find_type == 'id':
            WebDriverWait(self.driver, self.findElementsWaitTimeout).until(
                EC.presence_of_element_located((By.ID, element)))
        elif find_type == 'id_array':
            WebDriverWait(self.driver, self.findElementsWaitTimeout).until(
                EC.presence_of_all_elements_located((By.ID, element)))
        elif find_type == 'xpath':
            WebDriverWait(self.driver, self.findElementsWaitTimeout).until(
                EC.presence_of_element_located((By.XPATH, element)))
        elif find_type == 'name':
            WebDriverWait(self.driver, self.findElementsWaitTimeout).until(
                EC.presence_of_element_located((By.NAME, element)))
        else:
            raise Exception('Find Element is wrong')

    def date_select(self, departure_date, return_date=None):
        # Go to current month
        number_of_swipes_departure = cal.calenderswipe(departure_date)
        self.driver.press_keycode(61)

        # Swipe to target month
        for swipe in number_of_swipes_departure:
            self.driver.press_keycode(61)

        if not number_of_swipes_departure:
            monthlywidget = self.driver.find_element_by_xpath(
                '//androidx.recyclerview.widget.RecyclerView/android.view.View[1]').rect
        else:
            monthlywidget = self.driver.find_element_by_xpath(
                '//androidx.recyclerview.widget.RecyclerView/android.view.View[last()]').rect
        number_of_week = cal.number_of_weeks(departure_date)
        weeknum = cal.weeknumber(departure_date)
        weekday = cal.weekday(departure_date)
        x_cord = cal.x_cord(monthlywidget['x'], monthlywidget['width'], weekday)
        y_cord = cal.y_cord(monthlywidget['y'], monthlywidget['height'], weeknum, number_of_week)
        TouchAction(self.driver).tap(None, x_cord, y_cord, 1).perform()

        if return_date is None:
            try:
                self.driver.find_element_by_id('com.flyin.bookings:id/done_button').click()
            except Exception as e:
                logger.error('Could not locate Done button')
                logger.info(traceback.print_exc())
        else:
            iCount = self.driver.find_elements_by_xpath('//androidx.recyclerview.widget.RecyclerView/android.view.View')

            current_date = datetime.today()
            todaymonth = current_date.month
            departure_month = departure_date.month

            if departure_month == todaymonth:
                self.driver.press_keycode(61)
            else:
                for swipe in iCount:
                    self.driver.press_keycode(61)

            # swiping for return month
            number_of_swipes_return = cal.calenderswipe(return_date)
            return_swipe = len(number_of_swipes_return) - len(number_of_swipes_departure)

            for swipe in range(0, return_swipe):
                self.driver.press_keycode(61)

            monthlywidget = self.driver.find_element_by_xpath(
                '//androidx.recyclerview.widget.RecyclerView/android.view.View[last()]').rect
            number_of_week = cal.number_of_weeks(return_date)
            weeknum = cal.weeknumber(return_date)
            weekday = cal.weekday(return_date)
            x_cord = cal.x_cord(monthlywidget['x'], monthlywidget['width'], weekday)
            y_cord = cal.y_cord(monthlywidget['y'], monthlywidget['height'], weeknum, number_of_week)
            TouchAction(self.driver).tap(None, x_cord, y_cord, 1).perform()
            try:
                self.driver.find_element_by_id('com.flyin.bookings:id/done_button').click()
            except Exception as e:
                logger.error('Could not locate Done button')
                logger.info(traceback.print_exc())

    def flights_oneway_data(self, travel_type, origin_code, origin_city, origin_country, destination_code, destination_city, destination_country,
                            journey_type, departure_days, actions: dict, airlines: list, logger):
        try:
            extracted_data = []
            print(origin_city)
            print(destination_city)
            self.waitForElementPopUp(actions.get('select_flight_option'), 'id')
            self.driver.find_element_by_id(actions.get('select_flight_option')).click()

            # Click One Way Flight
            self.waitForElementPopUp(actions.get('one_way_toggle'), 'id')
            self.driver.find_element_by_id(actions.get('one_way_toggle')).click()

            # Enter Departure
            try:
                self.waitForElementPopUp(actions.get('departure'), 'id')
                self.driver.find_element_by_id(actions.get('departure')).click()
                enter_departure = self.driver.find_element_by_id(actions.get('search_box'))
                enter_departure.send_keys(origin_code)
                self.driver.execute_script('mobile: performEditorAction', {'action': 'search'})
                self.driver.find_element_by_xpath(
                    "//*[@resource-id='" + actions.get('country_code') + "' and @text='" + origin_code + "']").click()
            except Exception as e:
                logger.error('Source Location Not found. Please Enter correct routes.')

            # Enter Destination
            try:
                self.waitForElementPopUp(actions.get('destination'), 'id')
                self.driver.find_element_by_id(actions.get('destination')).click()
                enter_destination = self.driver.find_element_by_id(actions.get('search_box'))
                enter_destination.send_keys(destination_code)
                self.driver.execute_script('mobile: performEditorAction', {'action': 'search'})
                self.driver.find_element_by_xpath("//*[@resource-id='" + actions.get(
                    'country_code') + "' and @text='" + destination_code + "']").click()
            except Exception as e:
                logger.error('Destination Location Not found. Please Enter correct routes.')

            # Date Selection
            try:
                self.waitForElementPopUp(actions.get('travel_dates'), 'id')
                self.driver.find_element_by_id(actions.get('travel_dates')).click()
            except Exception as e:
                logger.error('Dates popped up vey early')

            try:
                departure_date = cal.Onward(departure_days)
                print(departure_date)
                self.date_select(departure_date)
            except Exception as e:
                logger.error('exception caught while selecting the dates')
                logger.info(traceback.print_exc())

            # Non Stop Flight
            try:
                self.waitForElementPopUp(actions.get('non_stop'), 'id')
                self.driver.find_element_by_id(actions.get('non_stop')).click()
            except Exception as e:
                logger.error('Non Stop toggle button element not found')
                logger.info(traceback.print_exc())

            # Press Search Button
            try:
                self.driver.find_element_by_id(actions.get('search_button')).click()
            except Exception as e:
                logger.error('Search Button not found')
                logger.info(traceback.print_exc())

            for airline in airlines:
                # Select Airlines
                try:
                    print(airline)
                    self.waitForElementPopUp("com.flyin.bookings:id/Fastest_layout", 'id')
                    self.driver.find_element_by_xpath("//android.widget.TextView[@resource-id='" + actions.get(
                        'select_airways') + "' and @text='" + airline + "']").click()
                except Exception as e:
                    logger.error('Airlines not found')
                    logger.info(traceback.print_exc())
                    extracted_data.append({
                        "source": "flyin",
                        "channel": "app",
                        "language": "EN",
                        "extraction_date": str(date.today()),
                        "POS":"KSA",
                        "journey_type": journey_type,
                        "trip_type": travel_type,
                        "departure_date": str(departure_date),
                        "return_date": "NA",
                        "origin_city": origin_city,
                        "destination_city": destination_city,
                        "origin_code": origin_code,
                        "destination_code": destination_code,
                        "origin_country": origin_country,
                        "destination_country": destination_country,
                        "airline": airline,
                        "departure_flight_number": "NA",
                        "return_flight_number": "NA",
                        "currency": "NA",
                        "base_price": "NA",
                        "taxes_and_fees": "NA",
                        "other_fees": "NA",
                        "vat": "NA",
                        "total_price": "NA"
                    })
                    continue

                # Select first flight
                try:
                    self.waitForElementPopUp(
                        "//androidx.recyclerview.widget.RecyclerView[@resource-id=\'com.flyin.bookings:id/recycler_flights\']/android.widget.LinearLayout[1]",
                        'xpath')
                    self.driver.find_element_by_xpath(
                        "//androidx.recyclerview.widget.RecyclerView[@resource-id=\'com.flyin.bookings:id/recycler_flights\']/android.widget.LinearLayout[1]").click()
                except Exception as e:
                    logger.error('Flight not found')
                    logger.info(traceback.print_exc())

                # Click Continue Button
                self.waitForElementPopUp(actions.get('continue_button'), 'id')
                self.driver.find_element_by_id(actions.get('continue_button')).click()
                self.driver.implicitly_wait(30)

                # Fetch Airline Code
                try:
                    self.waitForElementPopUp(actions.get('airline_code'), 'id')
                    airline_code = self.driver.find_element_by_id(actions.get('airline_code')).get_attribute('text')
                    airline_code = re.sub(r"[()]", "", airline_code)
                    airline_code = re.sub(r"[ ]", "", airline_code)
                except Exception as e:
                    logger.error('Airline Code not found')
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    airline_code = "NA"

                # Swipe Up
                self.waitForElementPopUp(actions.get('review_trip'), 'id')
                TouchAction(self.driver).press(x=513, y=1483).move_to(x=508, y=585).release().perform()
                # driver.swipe(start_x=513, start_y=1483, end_x=513, end_y=585)

                # Fetch Data Points
                try:
                    base_price = self.driver.find_element_by_id(actions.get('base_price')).get_attribute('text')
                    base_price = base_price.split(" ")[1]
                    # print("Base Price = " + base_price)
                except Exception as e:
                    logger.error('exception caught while finding base price')
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    base_price = "NA"

                try:
                    taxes_and_fees = self.driver.find_element_by_id(actions.get('taxes_and_fees')).get_attribute('text')
                    taxes_and_fees = taxes_and_fees.split(" ")[1]
                    # print("Taxes & Fees = " + taxes_and_fees)
                except Exception as e:
                    logger.error('exception caught while finding taxes and fees')
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    taxes_and_fees = "NA"

                try:
                    other_fees = self.driver.find_element_by_id(actions.get('other_fees')).get_attribute('text')
                    other_fees = other_fees.split(" ")[1]
                    # print("Other Fees = " + other_fees)
                except Exception as e:
                    logger.error('exception caught while finding other_fees')
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    other_fees = "NA"

                if travel_type == 'Domestic':
                    try:
                        vat = self.driver.find_element_by_id(actions.get('vat')).get_attribute('text')
                        vat = vat.split(" ")[1]
                        # print("VAT = " + vat)
                    except Exception as e:
                        logger.error('exception caught while finding vat')
                        logger.error(e)
                        logger.info(traceback.print_exc())
                        vat = "NA"
                else:
                    vat = "NA"

                try:
                    total_price = self.driver.find_element_by_id(actions.get('total_price')).get_attribute('text')
                    total_price = total_price.split(" ")[1]
                    # print("Total Price = " + total_price)
                except Exception as e:
                    logger.error('exception caught while finding total_price')
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    total_price = "NA"

                extracted_data.append({
                    "source": "flyin",
                    "channel": "app",
                    "language": "EN",
                    "extraction_date": str(date.today()),
                    "POS": "KSA",
                    "journey_type": journey_type,
                    "trip_type": travel_type,
                    "departure_date": str(departure_date),
                    "return_date": "NA",
                    "origin_city": origin_city,
                    "destination_city": destination_city,
                    "origin_code": origin_code,
                    "destination_code": destination_code,
                    "origin_country": origin_country,
                    "destination_country": destination_country,
                    "airline": airline,
                    "departure_flight_number": airline_code,
                    "return_flight_number": "NA",
                    "currency": "SAR",
                    "base_price": base_price,
                    "taxes_and_fees": taxes_and_fees,
                    "other_fees": other_fees,
                    "vat": vat,
                    "total_price": total_price
                })

                print("Data has been captured for:" + airline)

                # filename = parsed_hotel_name+"_"+time.strftime("%Y_%m_%d_%H%M%S")
                # self.driver.save_screenshot("/Users/mitesh.gala/PycharmProjects/applicationscraping/booking/screenshots/"+filename+".png")

                # Go back
                self.waitForElementPopUp('//android.widget.ImageButton[@content-desc="Navigate up"]', 'xpath')
                self.driver.find_element_by_xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()

                # DeSelect Airlines
                self.waitForElementPopUp(
                    "//android.widget.TextView[@resource-id='" + actions.get('select_airways') + "']", 'xpath')
                self.driver.find_element_by_xpath("//android.widget.TextView[@resource-id='" + actions.get(
                    'select_airways') + "' and @text='" + airline + "']").click()

            # Go back to search page
            try:
                self.waitForElementPopUp('//android.widget.ImageButton[@content-desc="Navigate up"]', 'xpath')
                self.driver.find_element_by_xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()
            except Exception as e:
                logger.error('Back Button not found')
                logger.info(traceback.print_exc())

            try:
                self.waitForElementPopUp(
                    '//android.view.ViewGroup[@resource-id="com.flyin.bookings:id/toolbar"]/android.widget.ImageButton[1]',
                    'xpath')
                self.driver.find_element_by_xpath(
                    '//android.view.ViewGroup[@resource-id="com.flyin.bookings:id/toolbar"]/android.widget.ImageButton[1]').click()
            except Exception as e:
                logger.error('Main Back Button not found')
                logger.info(traceback.print_exc())

        except Exception as e:
            traceback.print_exc()
        finally:
            return extracted_data

    def flights_return_data(self, travel_type, origin_code, origin_city, origin_country, destination_code, destination_city, destination_country,
                            journey_type, departure_days, return_days, actions: dict, airlines: list, logger):
        try:
            extracted_data = []
            print(origin_city)
            print(destination_city)
            self.waitForElementPopUp(actions.get('select_flight_option'), 'id')
            self.driver.find_element_by_id(actions.get('select_flight_option')).click()

            # Enter Departure
            try:
                self.waitForElementPopUp(actions.get('departure'), 'id')
                self.driver.find_element_by_id(actions.get('departure')).click()
                self.waitForElementPopUp(actions.get('search_box'), 'id')
                enter_departure = self.driver.find_element_by_id(actions.get('search_box'))
                enter_departure.send_keys(origin_code)
                self.driver.execute_script('mobile: performEditorAction', {'action': 'search'})
                self.waitForElementPopUp("//*[@resource-id='" + actions.get('country_code') + "' and @text='" + origin_code + "']", 'xpath')
                self.driver.find_element_by_xpath(
                    "//*[@resource-id='" + actions.get('country_code') + "' and @text='" + origin_code + "']").click()
            except Exception as e:
                logger.error('Source Location Not found. Please Enter correct routes.')

            # Enter Destination
            try:
                self.waitForElementPopUp(actions.get('destination'), 'id')
                self.driver.find_element_by_id(actions.get('destination')).click()
                self.waitForElementPopUp(actions.get('search_box'), 'id')
                enter_destination = self.driver.find_element_by_id(actions.get('search_box'))
                enter_destination.send_keys(destination_code)
                self.driver.execute_script('mobile: performEditorAction', {'action': 'search'})
                self.waitForElementPopUp("//*[@resource-id='" + actions.get(
                    'country_code') + "' and @text='" + destination_code + "']", 'xpath')
                self.driver.find_element_by_xpath("//*[@resource-id='" + actions.get(
                    'country_code') + "' and @text='" + destination_code + "']").click()
            except Exception as e:
                logger.error('Destination Location Not found. Please Enter correct routes.')

            # Date Selection
            try:
                self.waitForElementPopUp(actions.get('travel_dates'), 'id')
                self.driver.find_element_by_id(actions.get('travel_dates')).click()
            except Exception as e:
                logger.error('Dates popped up vey early')

            try:
                departure_date = cal.Onward(departure_days)
                print(departure_date)

                return_date = cal.Return(departure_date, return_days)
                print(return_date)

                self.date_select(departure_date, return_date)
            except Exception as e:
                logger.error('exception caught while selecting the dates')
                logger.info(traceback.print_exc())

            # Non Stop Flight
            try:
                self.waitForElementPopUp(actions.get('non_stop'), 'id')
                self.driver.find_element_by_id(actions.get('non_stop')).click()
            except Exception as e:
                logger.error('Non Stop toggle button element not found')
                logger.info(traceback.print_exc())

            # Press Search Button
            try:
                self.driver.find_element_by_id(actions.get('search_button')).click()
            except Exception as e:
                logger.error('Search Button not found')
                logger.info(traceback.print_exc())

            for airline in airlines:
                # Select Departure Airlines
                try:
                    print(airline)
                    self.waitForElementPopUp("com.flyin.bookings:id/Fastest_layout", 'id')
                    self.driver.find_element_by_xpath("//android.widget.TextView[@resource-id='" + actions.get(
                        'select_airways') + "' and @text='" + airline + "']").click()
                except Exception as e:
                    logger.error('Airlines not found')
                    logger.info(traceback.print_exc())
                    extracted_data.append({
                        "source": "flyin",
                        "channel": "app",
                        "language": "EN",
                        "extraction_date": str(date.today()),
                        "POS": "KSA",
                        "journey_type": journey_type,
                        "trip_type": travel_type,
                        "departure_date": str(departure_date),
                        "return_date": str(return_date),
                        "origin_city": origin_city,
                        "destination_city": destination_city,
                        "origin_code": origin_code,
                        "destination_code": destination_code,
                        "origin_country": origin_country,
                        "destination_country": destination_country,
                        "airline": airline,
                        "departure_flight_number": "NA",
                        "return_flight_number": "NA",
                        "currency": "NA",
                        "base_price": "NA",
                        "taxes_and_fees": "NA",
                        "other_fees": "NA",
                        "vat": "NA",
                        "total_price": "NA"
                    })
                    continue

                # Select first flight
                try:
                    self.waitForElementPopUp(
                        "//androidx.recyclerview.widget.RecyclerView[@resource-id=\'com.flyin.bookings:id/recycler_flights\']/android.widget.LinearLayout[1]",
                        'xpath')
                    self.driver.find_element_by_xpath(
                        "//androidx.recyclerview.widget.RecyclerView[@resource-id=\'com.flyin.bookings:id/recycler_flights\']/android.widget.LinearLayout[1]").click()
                except Exception as e:
                    logger.error('Flight not found')
                    logger.info(traceback.print_exc())

                # Click Continue Button
                self.waitForElementPopUp(actions.get('continue_button'), 'id')
                self.driver.find_element_by_id(actions.get('continue_button')).click()
                self.driver.implicitly_wait(30)

                # Select Return Airlines
                try:
                    print(airline)
                    self.waitForElementPopUp("com.flyin.bookings:id/Fastest_layout", 'id')
                    self.driver.find_element_by_xpath("//android.widget.TextView[@resource-id='" + actions.get(
                        'select_airways') + "' and @text='" + airline + "']").click()
                except Exception as e:
                    logger.error('Return airlines not found')
                    logger.info(traceback.print_exc())
                    extracted_data.append({
                        "source": "flyin",
                        "channel": "app",
                        "language": "EN",
                        "extraction_date": str(date.today()),
                        "POS": "KSA",
                        "journey_type": journey_type,
                        "trip_type": travel_type,
                        "departure_date": str(departure_date),
                        "return_date": str(return_date),
                        "origin_city": origin_city,
                        "destination_city": destination_city,
                        "origin_code": origin_code,
                        "destination_code": destination_code,
                        "origin_country": origin_country,
                        "destination_country": destination_country,
                        "airline": airline,
                        "departure_flight_number": "NA",
                        "return_flight_number": "NA",
                        "currency": "NA",
                        "base_price": "NA",
                        "taxes_and_fees": "NA",
                        "other_fees": "NA",
                        "vat": "NA",
                        "total_price": "NA"
                    })

                    self.waitForElementPopUp('//android.widget.ImageButton[@content-desc="Navigate up"]', 'xpath')
                    self.driver.find_element_by_xpath(
                        '//android.widget.ImageButton[@content-desc="Navigate up"]').click()

                    # DeSelect Airlines
                    self.waitForElementPopUp(
                        "//android.widget.TextView[@resource-id='" + actions.get('select_airways') + "']", 'xpath')
                    self.driver.find_element_by_xpath("//android.widget.TextView[@resource-id='" + actions.get(
                        'select_airways') + "' and @text='" + airline + "']").click()

                    continue

                # Select first flight
                try:
                    self.waitForElementPopUp(
                        "//androidx.recyclerview.widget.RecyclerView[@resource-id=\'com.flyin.bookings:id/recycler_flights\']/android.widget.LinearLayout[1]",
                        'xpath')
                    self.driver.find_element_by_xpath(
                        "//androidx.recyclerview.widget.RecyclerView[@resource-id=\'com.flyin.bookings:id/recycler_flights\']/android.widget.LinearLayout[1]").click()
                except Exception as e:
                    logger.error('Flight not found')
                    logger.info(traceback.print_exc())

                # Click Continue Button
                self.waitForElementPopUp(actions.get('continue_button'), 'id')
                self.driver.find_element_by_id(actions.get('continue_button')).click()
                self.driver.implicitly_wait(30)

                # Fetch Departure Airline Code
                try:
                    self.waitForElementPopUp(actions.get('img_onward'), 'id')
                    airline_code_departure = self.driver.find_element_by_id(actions.get('airline_code')).get_attribute('text')
                    airline_code_departure = re.sub(r"[()]", "", airline_code_departure)
                    airline_code_departure = re.sub(r"[ ]", "", airline_code_departure)
                except Exception as e:
                    logger.error('Airline Code not found')
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    airline_code_departure = "NA"

                # Fetch Return Airline Code
                try:
                    self.waitForElementPopUp(actions.get('img_return_flight'), 'id')
                    self.driver.find_element_by_id(actions.get('img_return_flight')).click()
                    airline_code_return = self.driver.find_element_by_id(actions.get('airline_code')).get_attribute('text')
                    airline_code_return = re.sub(r"[()]", "", airline_code_return)
                    airline_code_return = re.sub(r"[ ]", "", airline_code_return)
                except Exception as e:
                    logger.error('Airline Code not found')
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    airline_code_return = "NA"

                # Swipe Up
                self.driver.find_element_by_id(actions.get('img_return_flight')).click()

                # Fetch Data Points
                try:
                    base_price = self.driver.find_element_by_id(actions.get('base_price')).get_attribute('text')
                    base_price = base_price.split(" ")[1]
                except Exception as e:
                    logger.error('exception caught while finding base price')
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    base_price = "NA"

                try:
                    taxes_and_fees = self.driver.find_element_by_id(actions.get('taxes_and_fees')).get_attribute('text')
                    taxes_and_fees = taxes_and_fees.split(" ")[1]
                except Exception as e:
                    logger.error('exception caught while finding taxes and fees')
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    taxes_and_fees = "NA"

                try:
                    other_fees = self.driver.find_element_by_id(actions.get('other_fees')).get_attribute('text')
                    other_fees = other_fees.split(" ")[1]
                except Exception as e:
                    logger.error('exception caught while finding other_fees')
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    other_fees = "NA"

                if travel_type == 'Domestic':
                    try:
                        vat = self.driver.find_element_by_id(actions.get('vat')).get_attribute('text')
                        vat = vat.split(" ")[1]
                    except Exception as e:
                        logger.error('exception caught while finding vat')
                        logger.error(e)
                        logger.info(traceback.print_exc())
                        vat = "NA"
                else:
                    vat = "NA"

                try:
                    total_price = self.driver.find_element_by_id(actions.get('total_price')).get_attribute('text')
                    total_price = total_price.split(" ")[1]
                    # print("Total Price = " + total_price)
                except Exception as e:
                    logger.error('exception caught while finding total_price')
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    total_price = "NA"

                extracted_data.append({
                    "source": "flyin",
                    "channel": "app",
                    "language": "EN",
                    "extraction_date": str(date.today()),
                    "POS": "KSA",
                    "journey_type": journey_type,
                    "trip_type": travel_type,
                    "departure_date": str(departure_date),
                    "return_date": str(return_date),
                    "origin_city": origin_city,
                    "destination_city": destination_city,
                    "origin_code": origin_code,
                    "destination_code": destination_code,
                    "origin_country": origin_country,
                    "destination_country": destination_country,
                    "airline": airline,
                    "departure_flight_number": airline_code_departure,
                    "return_flight_number": airline_code_return,
                    "currency": "SAR",
                    "base_price": base_price,
                    "taxes_and_fees": taxes_and_fees,
                    "other_fees": other_fees,
                    "vat": vat,
                    "total_price": total_price
                })

                print("Data has been captured for:" + airline)

                # filename = parsed_hotel_name+"_"+time.strftime("%Y_%m_%d_%H%M%S")
                # self.driver.save_screenshot("/Users/mitesh.gala/PycharmProjects/applicationscraping/booking/screenshots/"+filename+".png")

                # Go back
                self.waitForElementPopUp('//android.widget.ImageButton[@content-desc="Navigate up"]', 'xpath')
                self.driver.find_element_by_xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()

                try:
                    self.waitForElementPopUp('com.flyin.bookings:id/close', 'id')
                    self.driver.find_element_by_id('com.flyin.bookings:id/close').click()
                except Exception as e:
                    logger.error('Cancel button  not found')
                    logger.info(traceback.print_exc())

                #if close_img:
                #    print(close_img)
                #    self.driver.find_element_by_id('com.flyin.bookings:id/close').click()


                self.waitForElementPopUp('//android.widget.ImageButton[@content-desc="Navigate up"]', 'xpath')
                self.driver.find_element_by_xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()

                # DeSelect Airlines
                self.waitForElementPopUp(
                    "//android.widget.TextView[@resource-id='" + actions.get('select_airways') + "']", 'xpath')
                self.driver.find_element_by_xpath("//android.widget.TextView[@resource-id='" + actions.get(
                    'select_airways') + "' and @text='" + airline + "']").click()

            # Go back to search page
            try:
                self.waitForElementPopUp('//android.widget.ImageButton[@content-desc="Navigate up"]', 'xpath')
                self.driver.find_element_by_xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()
            except Exception as e:
                logger.error('Back Button not found')
                logger.info(traceback.print_exc())

            try:
                self.waitForElementPopUp(
                    '//android.view.ViewGroup[@resource-id="com.flyin.bookings:id/toolbar"]/android.widget.ImageButton[1]',
                    'xpath')
                self.driver.find_element_by_xpath(
                    '//android.view.ViewGroup[@resource-id="com.flyin.bookings:id/toolbar"]/android.widget.ImageButton[1]').click()
            except Exception as e:
                logger.error('Main Back Button not found')
                logger.info(traceback.print_exc())

        except Exception as e:
            traceback.print_exc()
        finally:
            return extracted_data


if __name__ == '__main__':
    app_start_time = datetime.now()
    print("the start time is {}".format(str(app_start_time)))

    ##### Reading Metadata from GoogleSheets
    routes_data = gs.routes_data()

    ##### Defining Initial Parameters #####
    oneway_routes_data = routes_data.loc[(routes_data['Journey_Type'] == 'oneway')]
    return_routes_data = routes_data.loc[(routes_data['Journey_Type'] == 'return')]
    flyin_app = Flyinflights()
    utils = Utils()
    with open('flyin_flights_properties', 'r') as json_file:
        data = json.load(json_file)
    action_elements = data.get('details').get('elements')
    log_file_path = data.get('logging').get('log_file_path')
    logger = utils.getlogger(logging.INFO, log_file_path, 'flyin_data_scrap.info')
    logger.info('Starting')

    ##### Oneway flights #####
    try:
        desired_capabilities = flyin_app.createDesiredCapabilty()
        flyin_app.driver = webdriver.Remote(command_executor=data.get('appium').get('server_details'),
                                            desired_capabilities=desired_capabilities)
    except Exception as e:
        logger.error('Could not open application')

    oneway_flights = []
    for index, row in oneway_routes_data.iterrows():
        no_of_days = convert_string_to_list_of_tuples(row['Departure/Return Days'])
        airlines = list(row['Airlines'].split(","))
        for nod in no_of_days:
            departure_days = nod[0]
            flights_data = flyin_app.flights_oneway_data(row['Travel_Type'], row['Origin_Code'], row['Origin_City'], row['Origin_Country'],
                                                         row['Destination_Code'], row['Destination_City'], row['Destination_Country'],
                                                         row['Journey_Type'], departure_days, action_elements, airlines,
                                                         logger)
            oneway_flights.extend(flights_data)
    flyin_app.driver.quit()
    print("Final Oneway Data")
    print(oneway_flights)

    ##### Return flights #####
    try:
        desired_capabilities = flyin_app.createDesiredCapabilty()
        flyin_app.driver = webdriver.Remote(command_executor=data.get('appium').get('server_details'),
                                            desired_capabilities=desired_capabilities)
    except Exception as e:
        logger.error('Could not open application')

    return_flights = []
    for index, row in return_routes_data.iterrows():
        no_of_days = convert_string_to_list_of_tuples(row['Departure/Return Days'])
        airlines = list(row['Airlines'].split(","))
        for nod in no_of_days:
            departure_days = nod[0]
            return_days = nod[1]
            flights_data = flyin_app.flights_return_data(row['Travel_Type'], row['Origin_Code'], row['Origin_City'],row['Origin_Country'],
                                                         row['Destination_Code'], row['Destination_City'], row['Destination_Country'],
                                                         row['Journey_Type'], departure_days, return_days, action_elements, airlines,
                                                         logger)
            return_flights.extend(flights_data)
    flyin_app.driver.quit()
    print("Final Return Data")
    print(return_flights)

    flyin_data = []
    flyin_data.extend(oneway_flights)
    flyin_data.extend(return_flights)
    print("Final Flyin Data")
    print(flyin_data)
    #filename = utils.writeToFile(flyin_data, data.get('output_location'), 'flyin')
    #utils.saveToS3(filename)
    app_end_time = datetime.now()
    print("the end time is {}".format(str(app_end_time)))
    print("timetaken is {}".format(str(app_end_time - app_start_time)))
    logger.info('timetaken is {}'.format(str(app_end_time - app_start_time)))
