import logging
import os
from typing import Optional

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Optional
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

logger = logging.getLogger("clsroom.auth")
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler("./logs/auth.log")

logger.addHandler(c_handler)
logger.addHandler(f_handler)

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
    "https://www.googleapis.com/auth/classroom.topics.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


class Auth:
    def __init__(self):
        self.creds: Optional[Credentials] = None

    # TODO: Fix Invalid refresh token error
    def auth(self):
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except RefreshError:
                    logger.error("Refresh Error:", exc_info=True)
                finally:
                    flow = InstalledAppFlow.from_client_secrets_file("creds.json", SCOPES)
                    self.creds = flow.run_local_server(port=0)
            else:
                flow = InstalledAppFlow.from_client_secrets_file("creds.json", SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

        return self.creds
