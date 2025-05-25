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
        self.check_credentials()

    def check_credentials(self):
        """Check if the credentials file exists and load it."""
        if not os.path.exists("google_service_secret.json"):
            _gsc_json = settings.google_service_secret.replace("'", "\"")
            gsc_json = json.loads(_gsc_json)
            with open("google_service_secret.json", "w") as f:
                json.dump(
                    gsc_json,
                    f,
                    indent=4
                )

        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            "google_service_secret.json",
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
