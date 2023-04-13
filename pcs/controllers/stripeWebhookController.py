import json
from pcs.models.user import User
from pcs.models.stripeWebhook import StripeWebhook
from collections import OrderedDict
from pcs.util.stripe import stripe, get_webhook_key


user_model = User()
stripeWebhook_model = StripeWebhook()


def processHook(body, headers={}, event=None):
    payload = body
    sig_header = headers['Stripe-Signature'] if 'Stripe-Signature' in headers else str(headers)  # request.headers['STRIPE_SIGNATURE']

    # print("Body: ", body)

    try:
        if event == None:
            event = stripe.Webhook.construct_event(
                payload, sig_header, get_webhook_key()
            )
    except ValueError as e:  # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:  # Invalid signature
        raise e

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        stripe_event = json.loads(json.dumps(event)) #Allows event to be dumped out as a json
        stripeWebhook_model.create_or_replace(stripe_event)
        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)
        
        # print(payment_intent)
        
    elif event.type == 'payment_method.attached':
        payment_method = event.data.object  # contains a stripe.PaymentMethod
        stripe_event = json.loads(json.dumps(event)) #Allows event to be dumped out as a json
        stripeWebhook_model.create_or_replace(stripe_event)
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    # ... handle other event types

    elif event.type == 'customer.created':
        customer = event.data.object  # contains a stripe.Customer
        stripe_event = json.loads(json.dumps(event)) #Allows event to be dumped out as a json
        stripeWebhook_model.create_or_replace(stripe_event)
        # query = {"stripe_customer.id": customer.id}
        # user = user_model.get(userId)
        if not user:
            raise Exception("Could not find the user")
        print(customer)
        
    elif event.type == 'payment_intent.created':
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        stripe_event = json.loads(json.dumps(event)) #Allows event to be dumped out as a json
        stripeWebhook_model.create_or_replace(stripe_event)
        # print(payment_intent)
        
    elif event.type == 'customer.updated':
        customer = event.data.object  # contains a stripe.PaymentIntent
        stripe_event = json.loads(json.dumps(event)) #Allows event to be dumped out as a json
        stripeWebhook_model.create_or_replace(stripe_event)
        query = {"stripe_customer.id": customer.id}
        user = user_model.find(query)
        if not user:
            raise Exception("Could not find the user")
        print(customer)
        
    elif event.type == 'account.updated':
        account = event.data.object  # contains a stripe.Account
        stripe_event = json.loads(json.dumps(event)) #Allows event to be dumped out as a json
        stripeWebhook_model.create_or_replace(stripe_event)
        query = {"stripe_account.id": account.id}
        user = user_model.find(query)
        if not user: #Log to system
            raise Exception("Could not find the user")
        user['stripe_account'] = json.loads(str(account))
        return user_model.replace(user['id'], user)
    #TODO adding subscription_schedule. LOOK INTO
    else:
        print('Unhandled event type {}'.format(event.type))

def retryStripeEvent(eventId):
    #get the event
    event = stripeWebhook_model.get(eventId)
    #construct the event
    event = construct_event(json.dumps(event))
    #retry the webhook
    processHook(None, event=event)

def construct_event(payload):
    data = json.loads(payload, object_pairs_hook=OrderedDict)
    event = stripe.Event.construct_from(data, stripe.api_key)
    return event
