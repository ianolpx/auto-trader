import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from settings import settings
from handlers.utils.common import get_current_time


class WriterHandler:
    def __init__(self):
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        self.set_credentials()

    def set_credentials(self):
        _gsc_json = settings.google_service_secret.replace("'", "\"")
        gsc_json = json.loads(_gsc_json)

        self.creds = ServiceAccountCredentials.from_json_keyfile_dict(
            gsc_json,
            self.scope
        )

    def get_cursor(self):
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open("auto").sheet1
        return self.sheet


cursor = WriterHandler().get_cursor()


# python -m handlers.api.writer
if __name__ == "__main__":
    t = get_current_time()
    cursor.append_row([t, "자동 로그 기록"])
