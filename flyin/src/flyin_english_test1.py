import time
import datetime
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from flyin.src import flyin_calender as cal
import calendar

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


def swipecalender2(departure_date, return_date=None):
    # Go to current month
    number_of_swipes_departure = cal.calenderswipe(departure_date)
    driver.press_keycode(61)

    # Swipe to target month
    for swipe in number_of_swipes_departure:
        driver.press_keycode(61)

    if not number_of_swipes_departure:
        monthlywidget = driver.find_element_by_xpath(
            '//androidx.recyclerview.widget.RecyclerView/android.view.View[1]').rect
    else:
        monthlywidget = driver.find_element_by_xpath(
            '//androidx.recyclerview.widget.RecyclerView/android.view.View[last()]').rect
    number_of_week = cal.number_of_weeks(departure_date)
    weeknum = cal.weeknumber(departure_date)
    weekday = cal.weekday(departure_date)
    x_cord = cal.x_cord(monthlywidget['x'], monthlywidget['width'], weekday)
    y_cord = cal.y_cord(monthlywidget['y'], monthlywidget['height'], weeknum, number_of_week)
    TouchAction(driver).tap(None, x_cord, y_cord, 1).perform()

    if return_date is None:
        driver.find_element_by_id('com.flyin.bookings:id/done_button').click()
    else:
        iCount = driver.find_elements_by_xpath('//androidx.recyclerview.widget.RecyclerView/android.view.View')

        today = datetime.date.today()
        todaymonth = today.month
        departure_month = departure_date.month

        if departure_month == todaymonth:
            driver.press_keycode(61)
        else:
            for swipe in iCount:
                driver.press_keycode(61)

        # swiping for return month
        number_of_swipes_return = cal.calenderswipe(return_date)
        return_swipe = len(number_of_swipes_return) - len(number_of_swipes_departure)

        for swipe in range(0,return_swipe):
            driver.press_keycode(61)

        monthlywidget = driver.find_element_by_xpath(
            '//androidx.recyclerview.widget.RecyclerView/android.view.View[last()]').rect
        number_of_week = cal.number_of_weeks(return_date)
        weeknum = cal.weeknumber(return_date)
        weekday = cal.weekday(return_date)
        x_cord = cal.x_cord(monthlywidget['x'], monthlywidget['width'], weekday)
        y_cord = cal.y_cord(monthlywidget['y'], monthlywidget['height'], weeknum, number_of_week)
        TouchAction(driver).tap(None, x_cord, y_cord, 1).perform()
        driver.find_element_by_id('com.flyin.bookings:id/done_button').click()


driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_capability)
driver.implicitly_wait(10)

# driver.find_element_by_id('com.flyin.bookings:id/btn_continue').click()
# driver.find_element_by_id('com.flyin.bookings:id/txt_skip').click()
driver.find_element_by_id('com.flyin.bookings:id/rl_img_flight').click()

# One Way Flights
driver.find_element_by_id('com.flyin.bookings:id/txt_oneway').click()

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

# Date Selection
driver.find_element_by_id('com.flyin.bookings:id/tv_return_date_one').click()
# monthlywidget = driver.find_element_by_xpath('//androidx.recyclerview.widget.RecyclerView/android.view.View[1]').rect
# print(monthlywidget)
departure_date = cal.Onward(109)
#return_date = cal.Return(departure_date, 2)
print(departure_date)
#print(return_date)
swipecalender2(departure_date)


# Non Stop Flight
driver.find_element_by_id('com.flyin.bookings:id/non_stop').click()

# Press Search Button
driver.find_element_by_id('com.flyin.bookings:id/btn_flightsearch').click()
driver.implicitly_wait(30)

# Select Airlines
driver.find_element_by_xpath(
    '//android.widget.TextView[@resource-id="com.flyin.bookings:id/airways_name" and @text="Flynas"]').click()
driver.implicitly_wait(30)

# Select first flight
driver.find_element_by_xpath(
    '//androidx.recyclerview.widget.RecyclerView[@resource-id=\"com.flyin.bookings:id/recycler_flights\"]/android.widget.LinearLayout[1]').click()
driver.implicitly_wait(30)

# Click Continue Button
driver.find_element_by_id('com.flyin.bookings:id/btn_return_flights').click()
driver.implicitly_wait(30)
time.sleep(4)

# Swipe Up
TouchAction(driver).press(x=513, y=1483).move_to(x=508, y=585).release().perform()
# driver.swipe(start_x=513, start_y=1483, end_x=513, end_y=585)

# Fetch Data Points
base_price = driver.find_element_by_id('com.flyin.bookings:id/passenger_price').get_attribute('text')
print("Base Price = " + base_price)

taxes_and_fees = driver.find_element_by_id('com.flyin.bookings:id/tax_price').get_attribute('text')
print("Taxes & Fees = " + taxes_and_fees)

other_fees = driver.find_element_by_id('com.flyin.bookings:id/service_price').get_attribute('text')
print("Other Fees = " + other_fees)

vat = driver.find_element_by_id('com.flyin.bookings:id/vat_price').get_attribute('text')
print("VAT = " + vat)

total_price = driver.find_element_by_id('com.flyin.bookings:id/total_price').get_attribute('text')
print("Total Price = " + total_price)

time.sleep(2)

# Go back
driver.find_element_by_xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()
# DeSelect Airlines
driver.find_element_by_xpath(
    '//android.widget.TextView[@resource-id="com.flyin.bookings:id/airways_name" and @text="Flynas"]').click()
