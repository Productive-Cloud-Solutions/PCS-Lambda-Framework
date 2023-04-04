import uuid
import time
import json
from pcs.models.user import User
user_model = User()

class TestUser():

    def __init__(self, userId:str=None, type:str=None, name:str=None, firstName:str = None, 
                lastName:str=None, callback=None, gender:str=None, address:str=None, phone:str=None) -> None:
        # check if parameneter is passed or use default  
        self.id = userId if userId else str(uuid.uuid4())
        self.firstName = firstName if firstName else str(uuid.uuid4())[:6]
        self.lastName = lastName if lastName else str(uuid.uuid4())[:6]
        self.name = name if name else self.firstName + ' ' + self.lastName
        self.type = type if type else 'unspecified'
        self.username = str(uuid.uuid4())[:6]
        self.email = str(uuid.uuid4())[:6].strip("-")+"@gmail.com"
        self.gender = gender if gender else str(uuid.uuid4())[:4]
        self.address = address if address else {'city': 'Atlanta', 'county': None, 'line': 'Line', 'line2': None, 'state': 'GA', 'zip': None}
        self.phone = phone if phone else str(uuid.uuid4())[:10]

        # if not a function 
        if callback and not callable(callback):
            raise Exception("'callback' must be a function")
        # call the function 
        if callback:
            callback(self)

    @property
    def dbUser(self):
        return user_model.get(self.id)

    def __eq__(self, o) -> bool:
        return self.id == o.id

    
class LambdaTester():

    def __init__(self, handler) -> None:

        if handler and not callable(handler):
            raise Exception("'handler' must be a function")

        self.handler = handler
    
    def runEvent(self, event):
        ''' Runs an Already created event '''
        return self.handler(event, None)

    def createEvent(self, *argv, **kwargs):
        ''' Runs and creates the event '''
        return self.runEvent(createEvent(*argv, **kwargs))

    def buildEvent(self, *argv, **kwargs):
        ''' Only creates the event '''
        return createEvent(*argv, **kwargs)



def createEvent(action:str, payload:dict=None, user:TestUser = None, userId:str=None, 
    parentType:str=None, source:dict=None, _id:bool=False, 
    createdtTimeStamp:bool=True, modifiedTimeStamp:bool=True):
    # base Event 
    event = {
        "identity":{"claims": {"sub": "test-8004-443f-9c1b-66490ec68841"}, "sub": "test-8004-443f-9c1b-66490ec68841", "username": "2rf2erpfoilidec"},
        "action":action,
        'parentType':parentType if parentType else 'unspecified',
        'source':source if source else {},
    }

    event['info']={
        "parentTypeName":event['parentType'],
        "fieldName":event['action'],
    }

    uid = str(uuid.uuid4())
    # Default user ID
    event["identity"]["sub"] = uid
    event["identity"]["claims"]["sub"] = uid

    # if use user ID in event 
    if userId:
        event["identity"]["sub"] = userId
        event["identity"]["claims"]["sub"] = userId

    if user and not isinstance(user, TestUser):
        raise Exception("'user' must be of type 'TestUser'")
    
    if user:
        event["identity"]["sub"] = user.id
        event["identity"]["username"] = user.username
        event["identity"]["claims"]["sub"] = user.id

    # add payload to event 
    if payload:
        # if createdtTimeStamp is true or has a value 
        if createdtTimeStamp:
            # if createdtTimeStamp has a value use the value else create default timestamp im milliseconds
            payload["created"] = int(time.time()*1000) if createdtTimeStamp==True else createdtTimeStamp
        if modifiedTimeStamp:
            # if modifiedTimeStamp has a value use the value else create default timestamp im milliseconds
            payload["modified"] = int(time.time()*1000) if modifiedTimeStamp==True else modifiedTimeStamp
        if _id:
            # if _id has a value use the value else create new uuid
            payload["_id"] = str(uuid.uuid4()) if _id==True else _id
        event["payload"] = payload


    return event


def createUser(user:TestUser):
    # payload={
    # }
    userObj = {
        'id': user.id,
        'firstName': user.firstName,
        'lastName': user.lastName,
        'about': f'This is aboout {user.name} with {user.email}. Address: {user.address}.',
        'email': user.email,
    }
    # result = LambdaTester().createEvent("updateUser",payload=payload, user=user)
    result = user_model.create(userObj)
    result['type'] = user.type
    if user.gender:
        result['gender'] = user.gender
    if user.phone:
        result['phone'] = user.phone
    if user.address:
        result['address'] = user.address
    if user.name:
        result['name'] = user.name
    
    result = user_model.replace(user.id, result)
    return user

def loadSample(file):
    return json.load(open("test/test_data/"+file))