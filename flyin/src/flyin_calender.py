import datetime
import calendar
import monthdelta as monthdelta


def Onward(number_of_days):
    d = datetime.date.today()
    onward_date = d + datetime.timedelta(number_of_days)
    return onward_date


def Return(onward_date, days_of_return):
    return_date = onward_date + datetime.timedelta(days_of_return)
    return return_date


def calenderswipe(checkindate):
    today = datetime.date.today()
    currentmonth = today.month
    currentyear = today.year
    checkinmonth = checkindate.month
    checkinyear = checkindate.year
    num_months = (checkinyear - currentyear) * 12 + (checkinmonth - currentmonth)
    i = 1
    onemonthlater = today
    numofweekspermonth = []
    while i <= num_months:
        cal = calendar.TextCalendar(calendar.MONDAY).formatmonth(currentyear, currentmonth)
        numberofweeks = len(cal.split('\n')) - 3
        numofweekspermonth.append(numberofweeks)
        onemonthlater = onemonthlater + monthdelta.monthdelta(1)
        currentmonth = onemonthlater.month
        currentyear = onemonthlater.year
        i += 1
    return numofweekspermonth


def weeknumber(date):
    day = str(date.day)
    month = date.month
    year = date.year
    cal = calendar.TextCalendar(calendar.MONDAY).formatmonth(year, month)
    postString = cal.split("\n", 2)[2]
    week = postString.split('\n')
    weeknum = 0

    for i in week:
        pattern = i.find(day)
        if pattern != -1:
            weeknum = week.index(i) + 1
            break

    return weeknum


def number_of_weeks(date):
    month = date.month
    year = date.year
    cal = calendar.TextCalendar(calendar.MONDAY).formatmonth(year, month)
    numberofweeks = len(cal.split('\n')) - 3
    return numberofweeks


def weekday(date):
    weekday = date.weekday() + 1
    if weekday > 7:
        weekday = weekday - 7
    return weekday


def x_cord(x, width, weekday):
    x_axis = ((width / 7) * weekday) + x - (width / 14)
    return round(x_axis)


def y_cord(y, height, weeknum, totalweeks):
    y_axis = ((height / (totalweeks + 1)) * (weeknum + 1)) + y - (height / ((totalweeks + 1) * 2))
    return round(y_axis)


def monthend(date):
    year = date.year
    month = date.month
    day = date.day
    a = calendar.monthrange(year, month)
    weekday, days = a
    diff = days - day
    if diff < 2:
        return True
    return False


#departure_date = Onward(1)
#print(departure_date)
#b = Return(departure_date, 2)
#print(b)
