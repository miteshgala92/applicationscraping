import time
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
import calendar as cal

hotel_names = ['Kempinski Hotel Mall of the Emirates']
appwaitactivity = "com.flyin.bookings.activities.SplashScreenActivity"


desired_capability = {
    "platformName": "Android",
    "platformVersion": "11.0",
    "deviceName": "Android Emulator",
    "app": "/Users/mitesh.gala/MobileApps/Android/Flyin.apk",
    "appPackage": "com.flyin.bookings",
    "appWaitActivity": appwaitactivity,
    "noReset": "True"
}


driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_capability)
driver.implicitly_wait(10)

#driver.find_element_by_id('com.flyin.bookings:id/btn_continue').click()
#driver.find_element_by_id('com.flyin.bookings:id/txt_skip').click()
driver.find_element_by_id('com.flyin.bookings:id/rl_img_flight').click()

# Enter Departure
driver.find_element_by_id('com.flyin.bookings:id/linear_departure').click()
enter_departure = driver.find_element_by_id('com.flyin.bookings:id/et_search')
enter_departure.send_keys('JED')
driver.execute_script('mobile: performEditorAction', {'action': 'search'})
driver.find_element_by_xpath('//*[@resource-id="com.flyin.bookings:id/txt_countrycode" and @text="JED"]').click()

# Enter Destination

driver.find_element_by_id('com.flyin.bookings:id/linear_destination').click()
enter_departure = driver.find_element_by_id('com.flyin.bookings:id/et_search')
enter_departure.send_keys('RUH')
driver.execute_script('mobile: performEditorAction', {'action': 'search'})
driver.find_element_by_xpath('//*[@resource-id="com.flyin.bookings:id/txt_countrycode" and @text="RUH"]').click()

# Onward and Return Date
driver.find_element_by_id('com.flyin.bookings:id/tv_return_date_one').click()



# Non Stop Flight
# driver.find_element_by_id('com.flyin.bookings:id/non_stop').click()

# [0,484][1080,1794]
# [0,484][1080,1160]
# [0, 1160][1080, 1794]

# Press Search Button
#driver.find_element_by_id('com.flyin.bookings:id/btn_flightsearch').click()
