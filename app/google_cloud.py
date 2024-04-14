import json

from . import flask_app

from google.cloud import storage
from google.oauth2 import service_account


_credentials = service_account.Credentials.from_service_account_info(
    json.load(flask_app.config['GOOGLE_SERVICE_ACCOUNT_JSON_STRING']))
_storage_client = storage.Client(credentials=_credentials)
_bucket_name = flask_app.config['GOOGLE_STORAGE_BUCKET']


def _create_public_bucket(bucket_name: str):
    bucket = _storage_client.bucket(bucket_name)
    if not bucket.exists():
        _storage_client.create_bucket(bucket)
    policy = bucket.get_iam_policy()
    policy.bindings.append({"role": "roles/storage.objectViewer",
                            "members": {'allUsers'}})
    bucket.set_iam_policy(policy)
    bucket.configure_website("index.html", "404.html")
    bucket.patch()


def upload_blob_to_bucket(object_key: str, content: str, content_type: str):
    bucket = _storage_client.bucket(_bucket_name)
    if not bucket.exists():
        _create_public_bucket(_bucket_name)
    blob = bucket.blob(object_key)
    blob.upload_from_string(content, content_type=content_type)
    return 