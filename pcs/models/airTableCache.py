from pcs.models.baseModel import BaseModel
import time


class AirTableCache(BaseModel):

    def __init__(self) -> None:

        super().__init__("airtable-cache")


    def getCache(self, itemId):
        item = self.get(itemId)
        # if not in db 
        if not item:
            return None
        # if expired 
        if item['expire'] < time.time():
            return None
        
        return item['value']

    def setCache(self, key, item, expire=15):
        cacheObj={}
        cacheObj['id'] = key
        cacheObj['expire'] = time.time() + expire
        cacheObj['value'] = item
        return self.create_or_replace(cacheObj)