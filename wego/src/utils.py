from datetime import date, datetime
from datetime import timedelta
import json
import boto3
import os
import logging


class Utils:
    def __init__(self):
        self.weekend_weekday = 4

    def removeNonAscii(self, raw_string: str):
        return "".join(i for i in raw_string if ord(i) < 128)

    def getAlmatarFlightTravelDates(self, leg_type: str, onwards_days: int, return_days: int):
        if (leg_type == 'one_way'):
            return (str((date.today() + timedelta(onwards_days)).day),)
        else:
            return (str((date.today() + timedelta(onwards_days)).day), str((date.today() + timedelta(return_days)).day))

    def saveToS3(self, filepath):
        key_name = 'wego' + '_' + str(date.today())
        client = boto3.client('s3',
                              aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                              aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
                              )
        with open(filepath, 'rb') as data:
            client.upload_fileobj(data, 'stage-comp-price', 'data_scrapping/flights/{}'.format(key_name))

    def writeToFile(self, data, filepath, source, origin_code, destination_code, journey_type):
        today = datetime.now()
        folder_path = filepath + today.strftime('%Y-%m-%d')
        if not os.path.exists(folder_path):
            os.mkdir(folder_path, 0o777)
        folder_path = folder_path + "/"
        filename = origin_code + '_' + destination_code + '_' + journey_type + '_' + str(date.today()) + '.json'
        with open(folder_path + filename, 'w') as file_write:
            json.dump(data, file_write)
        return folder_path + filename

    def mergeFile(self, filepath, source):
        today = datetime.now()
        folder_path = filepath + today.strftime('%Y-%m-%d')
        print(folder_path)
        data = []
        for filename in os.listdir(folder_path):
            if filename.startswith('wego'):
                continue
            with open(os.path.join(folder_path, filename)) as infile:
                data.extend(json.load(infile))
        folder_path = folder_path + "/"
        filename = source + '_' + today.strftime('%Y-%m-%d') + '.json'
        with open(folder_path + filename, 'w') as file_write:
            json.dump(data, file_write)
        return folder_path + filename

    def getlogger(self, level, log_file_path, log_file_name):
        logger = logging.getLogger(__name__)
        logger.setLevel(level)
        current_date = str(date.today())
        ch = logging.FileHandler(log_file_path + current_date + '_' + log_file_name)
        ch.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - {SourceType} - {SourceName} - {SourceParameters} - %(name)s - %(levelname)s - %(message)s'.format(
                SourceType='<>', SourceName='<>',
                SourceParameters='<>'))
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

'''
if __name__ == '__main__':
    u = Utils()
    # flyin_data={"abc":"z"}
    output_location = "C:\\Users\\Admin\\PycharmProjects\\dt_data_scraping\\flyin\\target\\"
    # u.writeToFile(flyin_data, output_location, 'flyin',"JED","CAI","one_way")
    u.mergeFile(output_location, 'flyin')
'''