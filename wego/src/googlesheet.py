import json
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
with open('wego_properties') as json_file:
    data = json.load(json_file)

SAMPLE_SPREADSHEET_ID = data.get("SAMPLE_SPREADSHEET_ID")
SAMPLE_RANGE_NAME = data.get("SAMPLE_RANGE_NAME")

def routes_data():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(data.get("tokenpickel_location")):
        with open(data.get("tokenpickel_location"), 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(data.get('credentials_location'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(data.get('tokenpickel_location'), 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values')
    df = pd.DataFrame(values[1:], columns=values[0])
    df  = df.loc[(df['Active'] == 'YES')]

    if not values:
        print('No data found.')
        df = ''
        return df
    else:
        return df
