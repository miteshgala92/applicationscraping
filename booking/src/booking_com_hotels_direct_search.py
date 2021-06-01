import time

from appium import webdriver
from datetime import date,datetime
from time import sleep
from appium.webdriver.common.touch_action import TouchAction
from utils import Utils
import unicodedata
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.proxy import Proxy,ProxyType
import json
import logging


class BookingHotels:
    def __init__(self):
        self.apk_path='/Users/mitesh.gala/MobileApps/Android/Booking.apk'
        self.platformName='Android'
        self.devicename='Android Nexus 5'
        self.platformVersion='11.0'
        self.noReset=True
        self.driver=None
        self.checkin_date=None
        self.checkout_date=None
        self.findElementsWaitTimeout=40

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
            "appPackage":"com.booking",
            "appActivity": "com.booking.startup.HomeActivity",
            "noReset":self.noReset,
            "clearSystemFiles":True
        }
        return desired_capabilties

    def waitForElementPopUp(self,element:str,find_type:str):
        if(find_type=='id'):
            WebDriverWait(self.driver,self.findElementsWaitTimeout).until(EC.presence_of_element_located((By.ID,element)))
        elif (find_type == 'id_array'):
            WebDriverWait(self.driver, self.findElementsWaitTimeout).until(EC.presence_of_all_elements_located((By.ID, element)))
        elif(find_type=='xpath'):
            WebDriverWait(self.driver,self.findElementsWaitTimeout).until(EC.presence_of_element_located((By.XPATH,element)))
        elif(find_type=='name'):
            WebDriverWait(self.driver, self.findElementsWaitTimeout).until(EC.presence_of_element_located((By.NAME,element)))
        else:
            raise Exception('Find Element is wrong')


    def extract_hotels(self,meta_data:dict,utils,actions:dict,hotels_list:list,logger):
        try:
            dates_set_flag=False
            #commenting the below as setting the app as noreset
           # self.driver.find_element_by_id('com.booking:id/button_positive').click()
           # self.long_sleep()
           # self.driver.find_element_by_xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()
           # self.short_sleep()
            extracted_data=[]
            for hotel in hotels_list:
                self.waitForElementPopUp(actions.get('search_form'), 'id')
                self.driver.find_element_by_id(actions.get('search_form')).click()
                self.waitForElementPopUp(actions.get('search_city_text_box'), 'id')
                search_city = self.driver.find_element_by_id(actions.get('search_city_text_box'))
                search_city.send_keys(hotel.lower())
                self.waitForElementPopUp(actions.get('select_city'), 'id')
                self.driver.find_element_by_id(actions.get('select_city')).click()
                if(dates_set_flag==False):
                    try:
                        self.waitForElementPopUp(actions.get('select_dates'), 'id')
                        self.driver.find_element_by_id(actions.get('select_dates')).click()
                        #self.long_sleep()
                    except Exception as e:
                        logger.error('Dates popped up vey early')

                    try:
                        print(self.checkin_date, self.checkout_date)
                        print('//android.view.View[@content-desc="{}"]'.format(self.checkin_date))
                        self.driver.find_element_by_xpath(
                            '//android.view.View[@content-desc="{}"]'.format(self.checkin_date)).click()
                    except Exception as e:
                        logger.error("exception caught while selecting the dates")
                        logger.info(traceback.print_exc())
                        self.driver.swipe(start_x=580, start_y=800, end_x=580, end_y=300)
                        self.short_sleep()
                        self.driver.find_element_by_xpath(
                            '//android.view.View[@content-desc="{}"]'.format(self.checkin_date)).click()
                    try:
                        self.driver.find_element_by_xpath(
                            '//android.view.View[@content-desc="{}"]'.format(self.checkout_date)).click()
                    except Exception as e:
                        logger.error("exception caught while selecting the dates")
                        logger.info(traceback.print_exc())
                        self.driver.swipe(start_x=580, start_y=800, end_x=580, end_y=300)
                        self.short_sleep()
                        self.driver.find_element_by_xpath(
                            '//android.view.View[@content-desc="{}"]'.format(self.checkout_date)).click()


                    self.waitForElementPopUp(actions.get('calender_confirm'), 'id')
                    self.driver.find_element_by_id(actions.get('calender_confirm')).click()
                    dates_set_flag=True

                self.waitForElementPopUp(actions.get('search_button'), 'id')
                self.driver.find_element_by_id(actions.get('search_button')).click()
                try:
                    self.waitForElementPopUp(actions.get('hotel_names'),'id')
                    self.short_sleep()
                except Exception as e:
                    logger.error('exception caught at finding hotel')
                    logger.error(e)
                hotels_search_name = self.driver.find_elements_by_id(actions.get('hotel_names'))[0]
                try:
                    raw_name = hotels_search_name.text
                    parsed_hotel_name = (utils.removeNonAscii(raw_name)).replace('\n', '')
                    logger.info(parsed_hotel_name)
                except Exception as e:
                    logger.error(e)
                    logger.info(traceback.print_exc())
                try:
                    room_type = self.driver.find_elements_by_id(actions.get('main_page_room_type'))[0].text
                except Exception as e:
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    room_type="NA"
                try:
                    price = self.driver.find_elements_by_id(actions.get('view_price'))[0].text
                except Exception as e:
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    price="NA"
                try:
                    taxes = self.driver.find_elements_by_id(actions.get('tax_and_charges'))[0].text
                except Exception as e:
                    logger.error(e)
                    logger.info(traceback.print_exc())
                    taxes="NA"

                extracted_data.append({
                    "extraction_source": "booking.com",
                    "extraction_date":str(date.today()),
                    "checkin_date": self.checkin_date,
                    "checkout_date": self.checkout_date,
                    "city": meta_data.get('city'),
                    "hotel_name_searched": hotel,
                    "hotel_name_displayed": parsed_hotel_name,
                    "room_type": room_type,
                    # "currency":price.split(' ')[0],
                    "price": utils.removeNonAscii(price),
                    "taxes": utils.removeNonAscii(taxes)

                })
                print("Data has been captured")
                #hotels_list.remove(hotel)
                self.short_sleep()
                #print(actions.get('navigate_up'))
               # hotels_search_name.click()
                self.short_sleep()
                #filename = parsed_hotel_name+"_"+time.strftime("%Y_%m_%d_%H%M%S")
                #self.driver.save_screenshot("/Users/mitesh.gala/PycharmProjects/applicationscraping/booking/screenshots/"+filename+".png")
               # self.waitForElementPopUp('//android.widget.ImageButton[@content-desc="‎‏‎‎‎‎‎‏‎‏‏‏‎‎‎‎‎‏‎‎‏‎‎‎‎‏‏‏‏‏‎‏‏‎‏‏‎‎‎‎‏‏‏‏‏‏‏‎‏‏‏‏‏‎‏‎‎‏‏‎‏‎‎‎‎‎‏‏‏‎‏‎‎‎‎‎‏‏‎‏‏‎‎‏‎‏‎‏‏‏‏‏‎‎Navigate up‎‏‎‎‏‎"]', 'xpath')
                #self.driver.find_element_by_xpath('//android.widget.ImageButton[@content-desc="‎‏‎‎‎‎‎‏‎‏‏‏‎‎‎‎‎‏‎‎‏‎‎‎‎‏‏‏‏‏‎‏‏‎‏‏‎‎‎‎‏‏‏‏‏‏‏‎‏‏‏‏‏‎‏‎‎‏‏‎‏‎‎‎‎‎‏‏‏‎‏‎‎‎‎‎‏‏‎‏‏‎‎‏‎‏‎‏‏‏‏‏‎‎Navigate up‎‏‎‎‏‎"]').click()
                self.waitForElementPopUp('//android.widget.ImageButton[@content-desc="Navigate up"]', 'xpath')
                self.driver.find_element_by_xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()
                self.short_sleep()


            print("_____________________PRINTING THE FINAL PRICE_______________________")
            print(extracted_data)
        except Exception as e:
            traceback.print_exc()
        finally:
            self.driver.quit()
            return extracted_data

if __name__ == '__main__':
    hotel_city=["Al-Madinah"]
    for city in hotel_city:
        hotels_metadata = {'city': city}
        booking_app=BookingHotels()
        with open('booking_hotels_properties','r') as json_file:
            data=json.load(json_file)
        desired_capabilities = booking_app.createDesiredCapabilty()
        app_start_time=datetime.now()
        print("the start time is {}".format(str(app_start_time)))
        booking_app.driver = webdriver.Remote(command_executor=data.get('appium').get('server_details'),desired_capabilities=desired_capabilities)
        utils=Utils()
        dates=utils.getBookingComHotelSearchDates()
        booking_app.checkin_date=dates[0]
        booking_app.checkout_date=dates[1]
        print("the checking and checkout dates are dates are {} and {}".format(dates[0],dates[1]))



        action_elements=data.get('details').get('elements')
        log_file_path=data.get('logging').get('log_file_path')
        logger=utils.getlogger(logging.INFO,log_file_path,'hotel_data_scrap.info')
        hotels_list=data.get('city').get(hotels_metadata.get('city')).get('hotels_list')
        logger.info('Starting')
        logger.info('the list is {}'.format(hotels_list))
        print(hotels_list)
        scrapped_data=booking_app.extract_hotels(hotels_metadata,utils,action_elements,hotels_list,logger)
        filename=utils.writeToFile(scrapped_data,data.get('output_location'),'booking')
        utils.saveToS3(filename,hotels_metadata.get('city'))
        app_end_time=datetime.now()
        print("the end time is {}".format(str(app_end_time)))
        print("timetaken is {}".format(str(app_end_time-app_start_time)))
        logger.info('timetaken is {}'.format(str(app_end_time-app_start_time)))
        #logger.info("sleeping for while")
        #sleep(120)


   # booking_app.driver.get_window_size()


