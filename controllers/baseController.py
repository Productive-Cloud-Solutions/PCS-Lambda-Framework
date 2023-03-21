class BaseController():
    def __init__(self, userId=None, username=None, payload=None, source=None):
        self.userId = userId
        self.username = username
        self.payload = payload
        self.source = source
        self.user = self.userInit()

    def userInit(self):
        """
        Please Override in subclass
        to set the user object
        """
        return False

