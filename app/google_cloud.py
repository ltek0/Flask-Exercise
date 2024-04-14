import os

from google.cloud import storage
from google.oauth2 import service_account

credentials = service_account.Credentials.from_

storage_client = storage.Client(credentials=credentials)