import time
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from flyin.src import flyin_calender as cal


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


def swipecalender(num_of_weeks,monthlywidget:dict,y2):
    x = (monthlywidget.get('x') + monthlywidget.get('width')) / 2
    for i in range(0,num_of_weeks+1):
        print("swipe")
        #x = 99
        #y1 = monthlywidget.get('y')
        y1 = 1000
        #print(y1)
        #y2 = monthlywidget.get('y') + monthlywidget.get('height')
        y2 = y2
        #print(y2)
        #TouchAction(driver).press(x=x, y=y2).move_to(x=x, y=y1).release().perform()
        driver.swipe(start_x=x, start_y=y2, end_x=x, end_y=y1)
    time.sleep(3)

def swipecalender1(num_of_weeks, y1):
    x = 500
    print(y1)
    y1 = y1 + 175
    y2 = 1269
    if num_of_weeks == 5:
        y2 = y2 - 112
    elif num_of_weeks == 4:
        y2 = y2 - 224
    else:
        y2 = y2
    print(y2)

    #TouchAction(driver).press(x=x, y=y2).move_to(x=x, y=y1).release().perform()
    #TouchAction(driver).press(x=513, y=1283).move_to(x=508, y=1000).wait(3000).release().perform()
    driver.swipe(start_x=x, start_y=y2, end_x=x, end_y=y1)


driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_capability)
driver.implicitly_wait(10)

#driver.find_element_by_id('com.flyin.bookings:id/btn_continue').click()
#driver.find_element_by_id('com.flyin.bookings:id/txt_skip').click()
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
monthlywidget = driver.find_element_by_xpath('//androidx.recyclerview.widget.RecyclerView/android.view.View[1]').rect
#print(monthlywidget)
cal_date = cal.Onward(55)
print(cal_date)
number_of_swipes=cal.calenderswipe(cal_date)
print(number_of_swipes)
#calenderwidget = driver.find_element_by_id('com.flyin.bookings:id/day_picker').rect
temp = 0
for num_of_weeks in number_of_swipes:
    monthlywidget = driver.find_element_by_xpath('//androidx.recyclerview.widget.RecyclerView/android.view.View[1]').rect
    y2 = 1130 + temp
    swipecalender(num_of_weeks,monthlywidget,y2)
    temp = temp + 1
temp = 0
monthlywidget = driver.find_element_by_xpath('//androidx.recyclerview.widget.RecyclerView/android.view.View[1]').rect
#print(monthlywidget)
number_of_week_checkin = cal.number_of_weeks(cal_date)
#print(number_of_week_checkin)
weeknum_checkindate = cal.weeknumber(cal_date)
#print(weeknum_checkindate)
weekday_checkindate = cal.weekday(cal_date)
#print(weekday_checkindate)
x_cord_checkin = cal.x_cord(monthlywidget['x'],monthlywidget['width'],weekday_checkindate)
#print(x_cord_checkin)
y_cord_checkin = cal.y_cord(monthlywidget['y'],monthlywidget['height'],weeknum_checkindate,number_of_week_checkin)
#print(y_cord_checkin)
TouchAction(driver).tap(None, x_cord_checkin, y_cord_checkin, 1).perform()
driver.find_element_by_id('com.flyin.bookings:id/done_button').click()

# Non Stop Flight
driver.find_element_by_id('com.flyin.bookings:id/non_stop').click()

# Press Search Button
driver.find_element_by_id('com.flyin.bookings:id/btn_flightsearch').click()
driver.implicitly_wait(30)

#Select Airlines
driver.find_element_by_xpath('//android.widget.TextView[@resource-id="com.flyin.bookings:id/airways_name" and @text="Flynas"]').click()
driver.implicitly_wait(30)

#Select first flight
driver.find_element_by_xpath('//androidx.recyclerview.widget.RecyclerView[@resource-id=\"com.flyin.bookings:id/recycler_flights\"]/android.widget.LinearLayout[1]').click()
driver.implicitly_wait(30)

#Click Continue Button
driver.find_element_by_id('com.flyin.bookings:id/btn_return_flights').click()
driver.implicitly_wait(30)
time.sleep(4)

#Swipe Up
TouchAction(driver).press(x=513, y=1483).move_to(x=508, y=585).release().perform()
#driver.swipe(start_x=513, start_y=1483, end_x=513, end_y=585)

#Fetch Data Points
base_price = driver.find_element_by_id('com.flyin.bookings:id/passenger_price').get_attribute('text')
print("Base Price = "+base_price)

taxes_and_fees = driver.find_element_by_id('com.flyin.bookings:id/tax_price').get_attribute('text')
print("Taxes & Fees = "+taxes_and_fees)

other_fees = driver.find_element_by_id('com.flyin.bookings:id/service_price').get_attribute('text')
print("Other Fees = "+other_fees)

vat = driver.find_element_by_id('com.flyin.bookings:id/vat_price').get_attribute('text')
print("VAT = "+vat)

total_price = driver.find_element_by_id('com.flyin.bookings:id/total_price').get_attribute('text')
print("Total Price = "+total_price)

time.sleep(2)

#Go back
driver.find_element_by_xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()
#DeSelect Airlines
driver.find_element_by_xpath('//android.widget.TextView[@resource-id="com.flyin.bookings:id/airways_name" and @text="Flynas"]').click()
