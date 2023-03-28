import stripe
import json
import os
from . import secrets

API_KEY = json.loads(secrets.get_secret('dev/Stripe/Api'))

ENV = os.environ.get('ENVIRONMENT', 'dev')
if ENV == 'production':
    API_KEY = json.loads(secrets.get_secret('prod/Stripe/Api'))

stripe.api_key = API_KEY['secret']

def get_public_key():
    return API_KEY['public']
