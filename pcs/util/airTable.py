from pyairtable import Table as airTable
from pyairtable import Base as airBase
from pyairtable.formulas import *
import time
from models.airTableCache import AirTableCache
import hashlib 

airTableCache_model = AirTableCache()

API_LIMIT = 1.0 / 5  # 5 per second


def retry(max_retries = 6):
    def decorator(fn):
        """Decorator for functions that take Data and userId and checks if the user 
        exists. 
        """
        def wrapper(*args, **kwargs):
            sleepTime=API_LIMIT
            retries = 0
            for retries in range(max_retries):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    message = str(e)
                    if '429' not in message:
                        raise e # kill it, not a rate limit error
                    time.sleep(sleepTime)
                    sleepTime+=(API_LIMIT/2)

        return wrapper
    return decorator

class AirTableWrapper():

    def __init__(self, apikey) -> None:
        pass
        

class Table(airTable):

    def __init__(self, api_key: str, base_id: str, table_name: str, timeout=None):
        super().__init__(api_key, base_id, table_name, timeout=timeout)

    @retry()
    def create_or_update(self, fields: dict, formula, typecast=False):
        rec = self.first(formula=formula)
        # print('found',rec, 'for',formula)
        if rec:
            return super().update(rec['id'],fields,typecast)
        return super().create(fields, typecast)
    
    @retry()
    def get_or_create(self, fields: dict, formula, typecast=False):
        rec = self.first(formula=formula)
        # print('found',rec, 'for',formula)
        if rec:
            return rec
        return super().create(fields, typecast)

    @retry()
    def field_exists(self, field:str, dataType:str, value=None)->bool:
        typeMap = {
            'String':"Prob",
            'Attachment':[
                {
                    "url":'https://s3.us-east-2.amazonaws.com/assests.public.hbcu.3815/tech.png'
                }
            ],
            "Reference":"",
            "References":"",
            "SingleSelect":"",
            "Checkbox": True,
            'Number':20,
            "Date": "2021-01-13T22:30:00.000Z"
        }

        if dataType not in typeMap:
            return False
        
        try: # to create an obj with the field
            obj = {}
            obj[field] = typeMap[dataType]
            if value:
                obj[field] = value
            if isinstance(value, list) and dataType not in ["Reference", "References"]:
                for v in value:
                    obj[field] = v
                    result = self.create(obj)
                    self.delete(result['id'])
                return True
            result = self.create(obj)
            self.delete(result['id'])
            return True
        except Exception as e:
            # print(e)
            return False

    @retry()
    def find_and_delete_one(self,formula):
        rec = self.first(formula=formula)
        if rec:
            self.delete(rec['id'])
            return True
        return False

    @retry()
    def get(self, record_id: str):
        key = 'get_'+str(self.table_name)+str(record_id)
        key = str(hashlib.md5(key.encode()).hexdigest())

        cacheVal = airTableCache_model.getCache(key)
        # if cached 
        if cacheVal:
            return cacheVal

        # if no cache found 
        record = super().get(record_id)
        if record:
            airTableCache_model.setCache(key,record,60)

        return record

    @retry()
    def first(self, **options):
        key = 'first_'+str(self.table_name)+str(options)
        key = str(hashlib.md5(key.encode()).hexdigest())

        cacheVal = airTableCache_model.getCache(key)
        # if cached 
        if cacheVal:
            return cacheVal
        
        # if no cache found 
        record = super().first(**options)
        if record:
            airTableCache_model.setCache(key,record,60)
        
        return record

    @retry()
    def delete(self, record_id: str):
        return super().delete(record_id)

    @retry()
    def all(self, **options):
        key = 'all_'+str(self.table_name)+str(options)
        key = str(hashlib.md5(key.encode()).hexdigest())

        cacheVal = airTableCache_model.getCache(key)
        
        # if cached 
        if cacheVal:
            return cacheVal
        
        # if no cache found 
        record = super().all(**options)
        if record:
            airTableCache_model.setCache(key,record,60)
        
        return record

class Base(airBase):

    def __init__(self, api_key: str, base_id: str, timeout=None):
        super().__init__(api_key, base_id, timeout)

    @retry()
    def get_table(self,table_name:str):
        return Table(self.api_key,self.base_id,table_name)

    @retry()
    def table_exists(self, table_name):

        try:
            self.all(table_name)
            return self.get_table(table_name)
        except Exception as e:
            return False
    

def getField(record, field_name, default=None):
    if not record or "fields" not in record:
        return default
    
    fields = record['fields']
    
    if field_name not in fields:
        return default
    
    
    if isinstance(fields[field_name], list) and fields[field_name]:
        value = fields[field_name][0]

        #if image
        if "thumbnails" in value:
            return {
                "url": value['url'],
                "regular": value['thumbnails']['large']['url'],
                "thumbnailURL": value['thumbnails']['small']['url']
            }

    
    return fields[field_name]
