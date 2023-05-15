import uuid
import time
import json
from pcs.models.mongoWrapper import MongoWrapper

class TestUserModel(MongoWrapper):

    def __init__(self) -> None:

        super().__init__("test-user-table")
        
        
class TestUser():
    def __init__(self, user_model:MongoWrapper=None, **kwargs):
        self.__dict__.update(kwargs)
        # if hasattr(a, 'property'):
        #     a.property
        if user_model:
            if not isinstance(user_model, MongoWrapper):
                raise Exception("user_model must be instance of MongoWrapper")
            self.user_model =  user_model
        else:
            self.user_model =  TestUserModel()
        
        # If user id is given but id is not explicitly set
        if not hasattr(self, 'id'):
            self.id = self.userId if hasattr(self, 'userId') else str(uuid.uuid4())
        self.firstName = self.firstName if hasattr(self, 'firstName') else str(uuid.uuid4())[:6]
        self.lastName = self.lastName if hasattr(self, 'lastName') else str(uuid.uuid4())[:6]
        self.name = self.name if hasattr(self, 'name') else self.firstName + ' ' + self.lastName
        self.type = self.type if hasattr(self, 'type') else "To be specified"
        self.username = self.username if hasattr(self, 'username') else str(uuid.uuid4())[:6]
        self.email = self.email if hasattr(self, 'email') else str(uuid.uuid4())[:6].strip("-")+"@gmail.com"
        self.gender = self.gender if hasattr(self, 'gender') else str(uuid.uuid4())[:4]
        self.address = self.address if hasattr(self, 'address') else {'city': 'Atlanta', 'county': None, 'line': 'Line', 'line2': None, 'state': 'GA', 'zip': None}
        self.phone = self.phone if hasattr(self, 'phone') else str(uuid.uuid4())[:10]

    def set_user_model(self, user_model:MongoWrapper):
        if not isinstance(user_model, MongoWrapper):
            raise Exception("user_model must be instance of MongoWrapper")
        self.user_model=user_model
        
    @property
    def dbUser(self): 
        if not self.user_model:
            raise Exception("Please set user_model")
        return self.user_model.get(self.id)
    
    def createUser(self, user_model:MongoWrapper=None):
        if not user_model:
            return createUser(self.user_model, self)
        else:
            return createUser(user_model, self)

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


def createUser(user_model:MongoWrapper, user:TestUser):
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

