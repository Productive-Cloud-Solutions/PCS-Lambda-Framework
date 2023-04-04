import os
import time
from pcs.models.user import User
from pcs.util.stripe import stripe
from pcs.decorators.checkUser import check_user

user_model = User()

#Use paymentIntent to pass a payment
@check_user()
def createPaymentIntent(userId, data):
    amount = data.get('amount', None)
    if amount == None:
        raise Exception("Can't create payment (Payment Intent) without amount!")

    currency = data.get('currency', "usd")
    payment_method_types = data.get('payment_method_types', ["card"])
    
    # if empty list or not a list or first item is evaluatates to false
    if not payment_method_types or type(payment_method_types) != list or not payment_method_types[0]:
        raise Exception("Invalid Payment type(s)!")

    payment_method = data.get('payment_method', None)

    try:
        return stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            payment_method_types=payment_method_types,
        )
    except Exception as e:
        # print(e)
        raise Exception("Failed to create Payment (Payment Intent)!")

@check_user()
def cancelPaymentIntent(userId, data):

    intent_id = data.get('intentId', None)
    if intent_id == None:
        raise Exception("Can't cancel payment (Payment Intent) without Intent Id!")

    try:
        return stripe.PaymentIntent.cancel(
            intent_id,
        )
    except Exception as e:
        # print(e)
        raise Exception("Failed to cancel Payment (Payment Intent)!")

def connectStripe(user):

    if "stripe_account" in user:
        if user['stripe_account']['id']:
            return user

    account = stripe.Account.create(
        type = "express",
        # country = data['country'],
        email = user['email'],
        # api_key = stripe.api_key,
        business_type = 'individual',
        capabilities={
            "transfers": {"requested": True},
            # "card_payments": {"requested": True},
            },
        )
    user['stripe_account'] = account

    return user_model.replace(user['id'], user)

@check_user()
def getStripeOnboardingLink(user,data=None):

    if 'stripe_account' not in user:
        # __wrapped__ ignores the 
        user = connectStripe(user)
    
    accountLink = stripe.AccountLink.create(
        account = user['stripe_account']['id'],
        refresh_url = data.get('refresh_url',data.get('return_url')), #Get from front end
        return_url = data.get('return_url'), #Get from front end
        type = "account_onboarding"
    )
    return accountLink['url']

@check_user()
def getStripeLoginLink(user,data=None):

    if 'stripe_account' not in user:
        # __wrapped__ ignores the 
        user = connectStripe(user)
    
    accountLink = stripe.Account.create_login_link(
        user['stripe_account']['id'],
    )
    return accountLink['url']

@check_user()
def deleteStripeAccount(user,data=None):
    if 'stripe_account' not in user:
        return True
    
    result = stripe.Account.delete(user['stripe_account']['id'])

    del user['stripe_account']
    user_model.replace(user['id'], user)
    return result['deleted']
# Stripe Account Create
# stripe.Account.create()

# @check_user()
# def refundPayment(userId, data):

#     # charge_id = data.get('chargeId', None)
#     # if charge_id == None:
#         # raise Exception("Can't Refund payment without Charge Id")

#     intent_id = data.get('intentId', None)
#     if intent_id == None:
#         raise Exception("Can't Refund payment without Intent Id!")

#     try:
#         return stripe.Refund(
#             id = intent_id
#         )
#     except Exception as e:
#         # print(e)
#         raise Exception("Failed to Refund Payment!")