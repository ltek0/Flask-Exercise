from google.cloud import storage
from google.oauth2 import service_account

from . import flask_app

if flask_app.config['IS_DEV_LOCAL']:
    _storage_client = storage.Client(
        credentials = service_account.Credentials.from_service_account_file(
            filename = flask_app.config['GOOGLE_SERVICE_ACCOUNT_FILE']))
else:
    _storage_client = storage.Client()


def create_public_bucket(bucket_name: str):
    bucket = _storage_client.bucket(bucket_name)
    if not bucket.exists():
        _storage_client.create_bucket(bucket)
    policy = bucket.get_iam_policy()
    policy.bindings.append({"role": "roles/storage.objectViewer", "members": {'allUsers'}})
    bucket.set_iam_policy(policy)
    bucket.blob('404.html').upload_from_string("404 not found", content_type="text/html")
    bucket.blob('index.html').upload_from_string("Hello", content_type="text/html")
    bucket.configure_website("index.html", "404.html")
    bucket.patch()


def upload_blob_to_bucket(bucket_name: str, object_key: str, content: str, content_type: str):
    bucket = _storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name = object_key)
    blob.upload_from_string(data = content, content_type = content_type)
    return f"https://storage.googleapis.com/{bucket_name}/{object_key}"
