import re
import sys
from appium import webdriver
from datetime import date, datetime
from time import sleep
from appium.webdriver.common.touch_action import TouchAction
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from wego.src.utils import Utils
import wego.src.wego_calender as cal
import wego.src.googlesheet as gs
from selenium.webdriver.common.proxy import Proxy, ProxyType
import json
import logging
import easyocr
import re
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

def convert_string_to_list_of_tuples_for_airlines(days):
    no_of_days = []
    temp = []
    for token in days.split(","):
        num = token.replace("(", "").replace(")", "")
        temp.append(num)
        if ")" in token:
            no_of_days.append(tuple(temp))
            temp = []
    return no_of_days


class Wegoflights:
    def __init__(self):
        self.apk_path = '/Users/mitesh.gala/MobileApps/Android/Wego.apk'
        self.platformName = 'Android'
        self.devicename = 'Android Nexus 5'
        self.platformVersion = '11.0'
        self.noReset = True
        self.driver = None
        self.checkin_date = None
        self.checkout_date = None
        self.findElementsWaitTimeout = 30
        self.appwaitactivity = "com.wego.android.homebase.features.homescreen.HomeScreenBaseActivity"
        self.appPackage = "com.wego.android"

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
                expected_conditions.presence_of_element_located((By.ID, element)))
        elif find_type == 'id_array':
            WebDriverWait(self.driver, self.findElementsWaitTimeout).until(
                expected_conditions.presence_of_all_elements_located((By.ID, element)))
        elif find_type == 'xpath':
            WebDriverWait(self.driver, self.findElementsWaitTimeout).until(
                expected_conditions.presence_of_element_located((By.XPATH, element)))
        elif find_type == 'name':
            WebDriverWait(self.driver, self.findElementsWaitTimeout).until(
                expected_conditions.presence_of_element_located((By.NAME, element)))
        else:
            raise Exception('Find Element is wrong')

    def waitForElementPopUpAirlineSearch(self, element: str, find_type: str):
        if find_type == 'xpath':
            print(element)
            WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located((By.XPATH, element)))
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
                '//*[@resource-id="com.wego.android:id/pickerView"]/android.view.View[1]').rect
        else:
            monthlywidget = self.driver.find_element_by_xpath(
                '//*[@resource-id="com.wego.android:id/pickerView"]/android.view.View[1]').rect
        number_of_week = cal.number_of_weeks(departure_date)
        weeknum = cal.weeknumber(departure_date)
        weekday = cal.weekday(departure_date)
        x_cord = cal.x_cord(monthlywidget['x'], monthlywidget['width'], weekday)
        y_cord = cal.y_cord(monthlywidget['y'], monthlywidget['height'], weeknum, number_of_week)
        TouchAction(self.driver).tap(None, x_cord, y_cord, 1).perform()

    def flights_oneway_data(self, travel_type, origin_code, origin_city, origin_country, destination_code, destination_city, destination_country,
                            journey_type, departure_days, actions: dict, logger):
        global departure_date, extracted_data, no_of_booking_options
        no_of_adults=[1,2]
        try:
            extracted_data = []
            print(origin_city)
            print(destination_city)
            for noa in no_of_adults:
                print(f"No of adults: {noa:}")
                self.waitForElementPopUp(actions.get('select_flight_option'), 'id')
                self.driver.find_element_by_id(actions.get('select_flight_option')).click()

                # Click One Way Flight
                self.waitForElementPopUp(actions.get('one_way_toggle'), 'id')
                self.driver.find_element_by_id(actions.get('one_way_toggle')).click()

                # Enter Departure
                try:
                    self.waitForElementPopUp(actions.get('departure'), 'id')
                    self.driver.find_element_by_id(actions.get('departure')).click()
                    self.waitForElementPopUp(actions.get('search_box'), 'id')
                    enter_departure = self.driver.find_element_by_id(actions.get('search_box'))
                    enter_departure.send_keys(origin_code)
                    self.waitForElementPopUp("//*[@resource-id='" + actions.get('search_locations') + "']/android.widget.LinearLayout[1]",
                                             'xpath')
                    self.driver.find_element_by_xpath(
                        "//*[@resource-id='" + actions.get('search_locations') + "']/android.widget.LinearLayout[1]").click()
                except Exception as e:
                    logger.error('Source Location Not found. Please Enter correct routes.')

                # Enter Destination
                try:
                    self.waitForElementPopUp(actions.get('destination'), 'id')
                    self.driver.find_element_by_id(actions.get('destination')).click()
                    self.waitForElementPopUp(actions.get('search_box'), 'id')
                    enter_destination = self.driver.find_element_by_id(actions.get('search_box'))
                    enter_destination.send_keys(destination_code)
                    self.waitForElementPopUp(
                        "//*[@resource-id='" + actions.get('search_locations') + "']/android.widget.LinearLayout[1]",
                        'xpath')
                    self.driver.find_element_by_xpath(
                        "//*[@resource-id='" + actions.get(
                            'search_locations') + "']/android.widget.LinearLayout[1]").click()
                except Exception as e:
                    logger.error('Destination Location Not found. Please Enter correct routes.')

                # Date Selection
                try:
                    self.waitForElementPopUp(actions.get('departure_date'), 'id')
                    self.driver.find_element_by_id(actions.get('departure_date')).click()
                except Exception as e:
                    logger.error('Dates popped up vey early')

                try:
                    departure_date = cal.Onward(departure_days)
                    print(departure_date)
                    self.date_select(departure_date)
                except Exception as e:
                    logger.error('exception caught while selecting the dates')
                    logger.info(traceback.print_exc())

                # Select Number of Adults
                try:
                    self.waitForElementPopUp(actions.get('select_passengers'), 'id')
                    self.driver.find_element_by_id(actions.get('select_passengers')).click()
                    self.waitForElementPopUp(actions.get('select_adults'), 'id')
                    self.driver.find_element_by_id(actions.get('select_adults')).click()
                    self.waitForElementPopUp(f"//android.widget.TextView[{noa}]", 'xpath')
                    self.driver.find_element_by_xpath(f"//android.widget.TextView[{noa}]").click()
                    self.waitForElementPopUp(actions.get('passengers_done_button'), 'id')
                    self.driver.find_element_by_id(actions.get('passengers_done_button')).click()
                except Exception as e:
                    logger.error('Issue with passenger selection')
                    logger.info(traceback.print_exc())

                # Press Search Button
                try:
                    self.waitForElementPopUp(actions.get('search_button'), 'id')
                    self.driver.find_element_by_id(actions.get('search_button')).click()
                except Exception as e:
                    logger.error('Search Button not found')
                    logger.info(traceback.print_exc())

                sleep(40)

                # Edit Rate view
                try:
                    self.waitForElementPopUp(actions.get('rate_view_edit'), 'id')
                    self.driver.find_element_by_id(actions.get('rate_view_edit')).click()
                    self.waitForElementPopUp("//*[@resource-id='com.wego.android:id/title' and @text='Total Price']", 'xpath')
                    self.driver.find_element_by_xpath("//*[@resource-id='com.wego.android:id/title' and @text='Total Price']").click()
                    sleep(10)
                except Exception as e:
                    logger.error('Issue with passenger selection')
                    logger.info(traceback.print_exc())


                # Click on the flights
                try:
                    swipe_control = []

                    while len(swipe_control) < 30:
                        flight_rows = self.driver.find_elements_by_xpath(actions.get("row_flight_search_result_contents"))
                        #print(len(flight_rows))
                        #print(swipe_control)
                        loop_count=0

                        for i in flight_rows:
                            #print(i)
                            loop_count+=1
                            sleep(3)
                            try:
                                airline_name = self.driver.find_element_by_xpath("(" + actions.get("row_flight_search_result_contents") + ")" + f"[{loop_count}]" + "/android.widget.RelativeLayout/android.widget.TextView[@resource-id='com.wego.android:id/depart_airline_name']").get_attribute('text')
                                flight_start = self.driver.find_element_by_xpath("(" + actions.get("row_flight_search_result_contents") + ")" + f"[{loop_count}]" + "/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.TextView[@resource-id='com.wego.android:id/depart_flight_start']").get_attribute('text')
                                flight_search_depart_duration = self.driver.find_element_by_xpath("(" + actions.get("row_flight_search_result_contents") + ")" + f"[{loop_count}]" + "/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.TextView[@resource-id='com.wego.android:id/row_flight_search_depart_duration']").get_attribute('text')
                                flight_end = self.driver.find_element_by_xpath("(" + actions.get("row_flight_search_result_contents") + ")" + f"[{loop_count}]" + "/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.TextView[@resource-id='com.wego.android:id/depart_flight_end']").get_attribute('text')
                                provider_code = self.driver.find_element_by_xpath("(" + actions.get("row_flight_search_result_contents") + ")" + f"[{loop_count}]" + "/android.widget.TextView[@resource-id='com.wego.android:id/provider_code']").get_attribute('text')
                                dict = {"airline_name":airline_name,"flight_start":flight_start,"flight_search_depart_duration":flight_search_depart_duration,
                                       "flight_end":flight_end}
                                #print(dict)
                                if dict in swipe_control:
                                    continue
                                else:
                                    swipe_control.append(dict)
                            except Exception as e:
                                continue

                            try:
                                self.driver.find_element_by_xpath("(" + actions.get('row_flight_search_result_contents') + ")" + f"[{loop_count}]").click()
                            except Exception as e:
                                logger.error("not able to select flight")

                            # Wait for Number of booking options available and capture the count
                            try:
                                self.waitForElementPopUp(actions.get('booking_option_count'), 'id')
                                no_of_booking_options = self.driver.find_element_by_id(
                                    actions.get('booking_option_count')).get_attribute('text')
                                no_of_booking_options = int(no_of_booking_options.replace("(", "").replace(")", ""))
                            except Exception as e:
                                logger.error('Issue with number of bookings option')
                                logger.info(traceback.print_exc())


                            # Direct Non-Direct Flight
                            try:
                                self.driver.find_element_by_id(actions.get('flight_type'))
                                flight_type = "Non Direct"
                            except Exception as e:
                                flight_type = "Direct"
                            #print(flight_type)

                            # Before selecting first flight website
                            self.driver.press_keycode(61)
                            self.driver.press_keycode(61)
                            self.driver.press_keycode(61)

                            competitors = []
                            extracted_data_temp = {}
                            seller_rank = 0
                            # print(no_of_booking_options)
                            while len(competitors) < no_of_booking_options:
                                self.driver.press_keycode(61)
                                inner_loop_count = 0
                                for j in self.driver.find_elements_by_xpath("//*[@resource-id='" + actions.get('provider_name') + "' ]"):
                                    inner_loop_count+=1
                                    provider_name = self.driver.find_element_by_xpath("(//*[@resource-id='" + actions.get(
                                        'provider_name') + "' ])[" + str(inner_loop_count) + "]").get_attribute('text')
                                    if provider_name in competitors:
                                        continue
                                    else:
                                        competitors.append(provider_name)
                                    self.driver.find_element_by_xpath("(//*[@resource-id='" + actions.get(
                                        'flight_price_button') + "' ])[" + str(inner_loop_count) + "]").screenshot('price.png')
                                    reader = easyocr.Reader(['en'])
                                    output = reader.readtext('price.png')
                                    seller_price = re.findall(r'\d+', output[-1][1].replace("O", str(0)).replace("T", str(1)))
                                    seller_price = ''.join([str(elem) for elem in seller_price])
                                    # print(provider_name, seller_price)
                                    seller_rank += 1
                                    extracted_data_temp = {"source": "Wego",
                                                           "channel": "app",
                                                           "language": "EN",
                                                           "extraction_date": str(date.today()),
                                                           "POS":"KSA",
                                                           "journey_type": journey_type,
                                                           "trip_type": travel_type,
                                                           "departure_date":str(departure_date),
                                                           "return_date": "NA",
                                                           "origin_code":origin_code,
                                                           "origin_city":origin_city,
                                                           "origin_country":origin_country,
                                                           "destination_code":destination_code,
                                                           "destination_city":destination_city,
                                                           "destination_country":destination_country,
                                                           "pax":noa,
                                                           "airline_name":airline_name,
                                                           "flight_start":flight_start,
                                                           "flight_search_depart_duration":flight_search_depart_duration,
                                                           "flight_end":flight_end,
                                                           "flight_type":flight_type,
                                                           "currency": "SAR",
                                                           "seller_name":provider_name,
                                                           "seller_price":seller_price,
                                                           "seller_rank":seller_rank}
                                    # print(competitors)
                                    # print(len(competitors))
                                    extracted_data.append(extracted_data_temp)



                            # Press back button
                            self.waitForElementPopUp(actions.get('navigate_up'), 'id')
                            self.driver.find_element_by_id(actions.get('navigate_up')).click()
                            #sleep(5)
                            # print(swipe_control)

                        # Swipe
                        self.driver.swipe(start_x=523, start_y=1080, end_x=523, end_y=393)
                        sleep(2)
                except Exception as e:
                    logger.error('Issue with flight selection')
                    logger.info(traceback.print_exc())

                sleep(2)
                try:
                    self.driver.swipe(start_x=523, start_y=393, end_x=523, end_y=1080)
                    self.waitForElementPopUp('com.wego.android:id/icon', 'id')
                    self.driver.find_element_by_id('com.wego.android:id/icon').click()

                    self.waitForElementPopUp('com.wego.android:id/action_bar_nav_menu', 'id')
                    self.driver.find_element_by_id('com.wego.android:id/action_bar_nav_menu').click()
                except Exception as e:
                    logger.error('Back Button not found')
                    logger.info(traceback.print_exc())

        except Exception as e:
            traceback.print_exc()
        finally:
            return extracted_data


if __name__ == '__main__':
    app_start_time = datetime.now()
    print("the start time is {}".format(str(app_start_time)))
    with open('wego_properties', 'r') as json_file:
        data = json.load(json_file)
    sys.path.append('/Users/mitesh.gala/PycharmProjects/applicationscraping/wego/src')

    ##### Reading Metadata from GoogleSheets
    routes_data = gs.routes_data()

    ##### Defining Initial Parameters #####
    oneway_routes_data = routes_data.loc[(routes_data['Journey_Type'] == 'one_way')]
    wego_app = Wegoflights()
    utils = Utils()
    action_elements = data.get('details').get('elements')
    log_file_path = data.get('logging').get('log_file_path')
    logger = utils.getlogger(logging.INFO, log_file_path, 'wego_data_scrap.info')
    logger.info('Starting')

    ##### Oneway flights #####

    for index, row in oneway_routes_data.iterrows():
        no_of_days = convert_string_to_list_of_tuples(row['Departure/Return Days'])
        #airlines = list(row['Airlines'].split(","))
        oneway_flights = []
        try:
            desired_capabilities = wego_app.createDesiredCapabilty()
            wego_app.driver = webdriver.Remote(command_executor=data.get('appium').get('server_details'),
                                                desired_capabilities=desired_capabilities)

        except Exception as e:
            logger.error('Could not open application')
        for nod in no_of_days:
            departure_days = nod[0]
            flights_data = wego_app.flights_oneway_data(row['Travel_Type'], row['Origin_Code'], row['Origin_City'], row['Origin_Country'],
                                                         row['Destination_Code'], row['Destination_City'], row['Destination_Country'],
                                                         row['Journey_Type'], departure_days, action_elements,
                                                         logger)
            oneway_flights.extend(flights_data)
            print(oneway_flights)
        utils.writeToFile(oneway_flights, data.get('output_location'), 'wego', row['Origin_Code'], row['Destination_Code'], row['Journey_Type'])
    wego_app.driver.quit()

    filename = utils.mergeFile(data.get('output_location'), 'wego')
    utils.saveToS3(filename)

    app_end_time = datetime.now()
    print("the end time is {}".format(str(app_end_time)))
    print("timetaken is {}".format(str(app_end_time - app_start_time)))
    logger.info('timetaken is {}'.format(str(app_end_time - app_start_time)))
