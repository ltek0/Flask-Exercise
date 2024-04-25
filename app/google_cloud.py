from google.cloud import storage
from google.oauth2 import service_account

from . import flask_app


def _get_storage_client():
    if flask_app.config['IS_DEV_LOCAL']:
        return storage.Client(
            credentials=service_account.Credentials.from_service_account_file(
                filename=flask_app.config['GOOGLE_SERVICE_ACCOUNT_FILE']))
    else:
        return storage.Client()


def create_public_bucket(bucket: str):
    storage_client = _get_storage_client()
    bucket = storage_client.bucket(bucket)
    if not bucket.exists():
        storage_client.create_bucket(bucket)
    policy = bucket.get_iam_policy()
    policy.bindings.append(
        {"role": "roles/storage.objectViewer", "members": {'allUsers'}})
    bucket.set_iam_policy(policy)
    bucket.blob('404.html').upload_from_string(
        "404 not found", content_type="text/html")
    bucket.blob('index.html').upload_from_string(
        "Hello", content_type="text/html")
    bucket.configure_website("index.html", "404.html")
    bucket.patch()


def get_bucket():
    bucket = _get_storage_client().bucket(
        flask_app.config['GOOGLE_STORAGE_BUCKET'])
    if not bucket.exists():
        create_public_bucket(flask_app.config['GOOGLE_STORAGE_BUCKET'])
        bucket = _get_storage_client().bucket(
            flask_app.config['GOOGLE_STORAGE_BUCKET'])
    return bucket


def delete_from_object_key(object_key: str):
    print(f"Deleting {object_key}")
    bucket = _get_storage_client().bucket(
        flask_app.config['GOOGLE_STORAGE_BUCKET'])
    blob = bucket.blob(object_key)
    blob.delete()


class BucketObject(object):
    _bucket = get_bucket()

    def __init__(self, object_key: str):
        self.obj = object_key

    @property
    def exist(self) -> bool:
        o = self._bucket.blob(self.obj)
        if not o.exists():
            return False
        return True

    def upload(self, content: str, content_type: str):
        blob = self._bucket.blob(blob_name=self.obj)
        blob.upload_from_string(data=content, content_type=content_type)

    def delete(self):
        blob = self._bucket.blob(blob_name=self.obj)
        if self.exist:
            blob.delete()