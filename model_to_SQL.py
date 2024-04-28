# load env must be placed before app import
from dotenv import load_dotenv
load_dotenv('.flaskenv')

from app import flask_app, db
from sqlalchemy.schema import CreateTable

flask_app.app_context().push()

schema = ""

tables = db.metadata.tables.keys()
for table in tables:
    table = db.metadata.tables[table]
    schema += str(CreateTable(table).compile(db.engine))
schema = [line for line in schema.split('\n') if line.strip()]
schema = '\n'.join(schema)
print(schema.replace(' WITHOUT TIME ZONE', ''))
