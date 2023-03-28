import os
import json
from util import secrets
from util.airTable import Base, match

HERE = os.path.dirname(os.path.abspath(__file__))

SCHEMA = json.load(open(os.path.join(HERE, 'airTableSchema.json')))

API_KEY = json.loads(secrets.get_secret('prod/Airtable/API'))['key']
ENV = os.environ.get('ENVIRONMENT', 'dev')
BASE = Base(API_KEY, SCHEMA['base_id'][ENV])

def getSchema():
    return SCHEMA

def getBase():
    return BASE