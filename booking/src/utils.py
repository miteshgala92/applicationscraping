from datetime import date
from datetime import timedelta
import json
import boto3
import os
import logging

class Utils:
    def __init__(self):
        self.weekend_weekday=4

    def getUpCommingWeekend(self):
        if(date.today().weekday()>self.weekend_weekday):
            weekend_date = (date.today()+timedelta(2)) + timedelta(self.weekend_weekday - ((date.today()+timedelta(2)).weekday()))
            return ((weekend_date), (weekend_date + timedelta(days=2)))
        else:
            weekend_date=date.today()+timedelta(self.weekend_weekday-(date.today().weekday()))
            return ((weekend_date),(weekend_date+timedelta(days=2)))

    def getBookingComHotelSearchDates(self):
        weekend_dates=self.getUpCommingWeekend()
        return (str(weekend_dates[0].strftime('%d %B %Y')),str(weekend_dates[1].strftime('%d %B %Y')))

    def removeNonAscii(self,raw_string:str):
        return "".join(i for i in raw_string if ord(i) < 128)

    def flightExtractionDates(self,next_departure_days,next_return_days):
        return (date.today()+timedelta(days=next_departure_days),date.today()+timedelta(next_return_days))

    def getRehlatFlightTravelDates(self):
        pass

    def getAlmatarFlightTravelDates(self,leg_type:str,onwards_days:int,return_days:int):
        if(leg_type=='one_way'):
            return (str((date.today()+timedelta(onwards_days)).day),)
        else:
            return (str((date.today()+timedelta(onwards_days)).day),str((date.today()+timedelta(return_days)).day))

    def saveToS3(self,filepath,city_name):
        key_name='booking'+'_{}'.format(city_name)+'_'+str(date.today())
        client=boto3.client('s3',
                            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
                            )
        with open(filepath,'rb') as data:
            client.upload_fileobj(data,'stage-comp-price','data_scrapping_poc/hotels/{}'.format(key_name))

    def writeToFile(self,data,filepath,source):
        filename=source+'_'+str(date.today())
        with open(filepath+filename,'w') as file_write:
            json.dump(data,file_write)
        return filepath+filename

    def getlogger(self,level,log_file_path,log_file_name):
        logger = logging.getLogger(__name__)
        logger.setLevel(level)
        current_date = str(date.today())
        ch = logging.FileHandler(log_file_path+current_date+'_'+log_file_name)
        ch.setLevel(level)
        formatter = logging.Formatter(
                '%(asctime)s - {SourceType} - {SourceName} - {SourceParameters} - %(name)s - %(levelname)s - %(message)s'.format(
                    SourceType='<>', SourceName='<>',
                    SourceParameters='<>'))
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

'''if __name__ == '__main__':
    u=Utils()
    print(u.getBookingComHotelSearchDates())
    print(u.getAlmatarFlightTravelDates('2way',3,2))
'''

