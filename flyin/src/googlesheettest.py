import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1PFGCxQukL84EOlOkvdncQaOTmzluDm9DjOR8nwpBp8A'
SAMPLE_RANGE_NAME = 'Flyin_Flights!A1:I'

def routes_data():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('/Users/mitesh.gala/PycharmProjects/applicationscraping/flyin/credentials/token.pickle'):
        with open('/Users/mitesh.gala/PycharmProjects/applicationscraping/flyin/credentials/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/Users/mitesh.gala/PycharmProjects/applicationscraping/flyin/credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('/Users/mitesh.gala/PycharmProjects/applicationscraping/flyin/credentials/token.pickle', 'wb') as token:
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
