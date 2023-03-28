from models.user import User
# from models.baseModel import PermissionsBaseModel
from functools import wraps

user_model = User()

#TODO Make decorator taht can take in a list of account types ['manager', 'admin']
def check_user(types=[]):
    def decorator(fn):
        """Decorator for functions that take Data and userId. It checks if the user 
        exists and if it is either an manager or an admin. 
        """
        def wrapper(userId, data):
            user = user_model.get(userId)
            if not user:
                raise Exception('User Account could not be found!!!')
            
            if not types:
                return fn(user, data)
            
            if 'type' in user and user['type'] in types:
                return fn(user, data)
            else:
                raise Exception("Invalid Permissions!!!")

            # return fn(user, data)

        return wrapper
    return decorator