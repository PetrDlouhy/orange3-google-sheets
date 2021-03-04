import re
import pathlib
from Orange.data.io_base import DataTableMixin
from Orange.data.io import FileFormat

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GSheetWriter(FileFormat, DataTableMixin):
    @classmethod
    def open_sheet(cls, creds_token=None):
        credentials_file_name = pathlib.Path().absolute() + '/credentials.json'
        print(credentials_file_name)
        creds = None
        # The file token.pickle stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes
        # for the first time.
        if creds_token:
            creds = creds_token
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file_name, SCOPES)
                creds = flow.run_local_server(port=0)
        service = build('sheets', 'v4', credentials=creds)
        # Call the Sheets API
        return service, creds

    @classmethod
    def write_sheet(
        cls, data, spreadsheet_url,
        delete_sheet_content, creds_token, with_annotations=True,
    ):
        service, creds_token = cls.open_sheet(creds_token)
        match = re.match(r'(?:https?://)?(?:www\.)?'
                         r'docs\.google\.com/spreadsheets/d/'
                         r'(?P<output_spreadsheet_id>[-\w_]+)'
                         r'(?:/.*?gid=(?P<sheet_id>\d+).*|.*)?',
                         spreadsheet_url, re.IGNORECASE)
        try:
            output_spreadsheet_id = match.group('output_spreadsheet_id')
            if not output_spreadsheet_id:
                raise ValueError
            sheet_id = match.group('sheet_id') or 0
        except (AttributeError, ValueError):
            raise ValueError
        if delete_sheet_content:
            rangeAll = f'{sheet_id}!A1:ZZ'
            service.spreadsheets().values().clear(
                spreadsheetId=output_spreadsheet_id,
                body={},
                range=rangeAll,
            ).execute()

        class SheetWriter():
            paste_data = ""

            def writerow(self, data):
                self.paste_data += ",".join(data)
                self.paste_data += "\n"

        writer = SheetWriter()

        cls.write_headers(writer.writerow, data, with_annotations)
        cls.write_data(writer.writerow, data)

        requests = [{
         "pasteData": {
          "data": writer.paste_data,
          "type": "PASTE_NORMAL",
          "delimiter": ",",
          "coordinate": {
           "sheetId": sheet_id,
           "rowIndex": 0,
           "columnIndex": 0,
          }
         }
        }]
        body = {
            'requests': requests
        }
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=output_spreadsheet_id,
            body=body).execute()
        print("Google response: ", response.get('replies'))
        return creds_token
