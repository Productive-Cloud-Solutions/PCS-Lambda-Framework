import os
import boto3
import copy
# importing ObjectId from bson library
from bson.objectid import ObjectId
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import CollectionInvalid
from pcs.util import secrets
import urllib.parse
import json
import time
import uuid
import hashlib

def validate(fn):
    """Decorator for functions that take Data and userId and checks if the user 
    exists. 
    """
    def wrapper(data, userId):
        # user = user_model.getUser(userId, None)
        # if not user:
        #     raise Exception('User Account could not be found!!!')

        result = fn(data, userId)
        return result
    return wrapper


class MongoWrapper:
    
    def __init__(self, table, host = None) -> None:
        self.table = table
        self.collection_indexes = []
        MAIN_DB='main-mongo-database'
        host = os.environ.get('MONGO_DB_HOST')

        if os.environ.get('AWS_SAM_LOCAL'):
            client = MongoClient('local-db', 27017)
            self.db = client[MAIN_DB]
            # print('Local DB')
        else:
            if os.environ.get('ENVIRONMENT') == 'production':
                DBDATA = json.loads(secrets.get_secret('ProdBDAppSecret', region_name = "us-east-1"))
                username = urllib.parse.quote_plus(DBDATA['username'])
                password = urllib.parse.quote_plus(DBDATA['password'])

                HERE = os.path.dirname(os.path.abspath(__file__))
                pemFilePath = os.path.join(HERE, 'rds-combined-ca-bundle.pem')
                # conn = 'mongodb://%s:%s@%s/?tls=true&tlsCAFile=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false' % (username, password, DBDATA['host'])
                conn = 'mongodb://%s:%s@%s/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false' % (username, password, DBDATA['host'])
                client = MongoClient(conn, 
                                    tls=True,
                                    tlsCAFile=pemFilePath)
                self.db = client[MAIN_DB]
            else:
                client = MongoClient(host, 27017)
                self.db = client[MAIN_DB]

        # {
        #     "index": {},
        #     "options": {
        #         "unique": True,
        #     },

        # }
    def updateIndexes(self):
        indexes = self.db[self.table].list_indexes()
        index_name_list = []
        collection_hash_list = []
        for i in indexes:
            index_name_list.append(i['name'])

        
        # Check in collection_indexes are in the indexes of the table. If not then add them.
        for col_index in self.collection_indexes:
            index = []
            for k,v in col_index['index'].items():
                index.append((k,v))
            name = self.__indexHash(col_index['index'])
            collection_hash_list.append(name)
            if name not in index_name_list:
                self.db[self.table].create_index(index, name=name,  **col_index['options'])
        
        indexes = self.db[self.table].list_indexes()

        # Check if all the indexes of the table are in the collection index. If not then delete it.
        for i in indexes:
            if i['name'] != "_id_" and i['name'] not in collection_hash_list:
                self.db[self.table].drop_index(i)


    def __toDBID(self, val):
        try:
            return ObjectId(str(val))
        except:
            return str(val)

    def __convertToObjectId(self, obj):
        # convert id:12343 => _id: ObjectId(12343)
        if '_id' in obj:
            obj['_id'] = self.__toDBID(obj['_id'])
            return obj

        if 'id' in obj:
            obj['_id'] = self.__toDBID(obj['id'])
            del obj['id']
        return obj
            
    def __convertToId(self, obj):
        # convert _id: ObjectId(12343) => id:12343 
        if '_id' in obj:
            obj['id'] = str(obj['_id'])
            del obj['_id']
        return obj


    def create(self, item, projection=False):
        return self.put(item, projection)

    def create_or_replace(self, item):
        # if no id present create
        if 'id' not in item and '_id' not in item:
            return self.create(item)
        
        # id is present 
        item = self.__convertToId(item)
        obj = self.get(item['id'])

        # if not in database create it!
        if not obj:
            return self.create(item)
        # if is in database replace it!
        if obj:
            return self.replace(obj['id'],item)
        
        return False

    def put(self, item, projection=False):
        newItem = copy.deepcopy(item)
        # To go from python to low-level format
        result = self.db[self.table].insert_one(self.__convertToObjectId(newItem))
        if not result.acknowledged:
            return False
        
        return self.get(str(result.inserted_id), projection)

    def get(self, itemId, projection=False):
        result = self.db[self.table].find_one({
            '_id': self.__toDBID(itemId) 
        })
        if not result:
            return False
        
        return self.__convertToId(result)

    def find(self, query, projection=False):

        result = self.db[self.table].find_one(query)
        if not result :
            return False

        return self.__convertToId(result)
        
    def delete(self, itemId, projection=False):
        result = self.db[self.table].find_one_and_delete({
            '_id': self.__toDBID(itemId)
        })
        if not result:
            return False

        return self.__convertToId(result)

    def replace(self, itemId, item, projection=False):
        newItem = copy.deepcopy(item)
        result = self.db[self.table].replace_one({
            '_id': self.__toDBID(itemId)
        }, self.__convertToObjectId(newItem))

        if not result.acknowledged:
            return False

        return self.get(itemId,projection)

    def update(self, itemId, updateExpression):
        result = self.db[self.table].update_one({
                '_id': self.__toDBID(itemId)
            }, updateExpression)
        if not result.acknowledged:
            return False

        return self.get(itemId)
    

    def putMany(self, items, projection=False):
        converted = []
        for item in list(items):
            converted.append(self.__convertToObjectId(item))
        # insert many objects to collection
        result = self.db[self.table].insert_many(converted)

        if not result.acknowledged:
            return False
        
        return [str(obj_id) for obj_id in result.inserted_ids]

    def insertMany(self, items, projection=False):
        return self.putMany(items, projection)

        #Just an Alias for getItems
    def findMany(self, query, projection=False):
        """
        Alias for getItems
        """
        return self.getMany(query, projection=False)

    def getMany(self, query, projection=False):
        result = self.db[self.table].find(self.__convertToObjectId(query))
        if not result:
            return result

        converted = []
        for item in list(result):
            converted.append(self.__convertToId(item))

        return converted

 

    def find_one_and_update(self, query, updateExpression):
    
        result = self.db[self.table].find_one_and_update(query, updateExpression, return_document=ReturnDocument.AFTER)
        if not result :
            return False
        return self.__convertToId(result) 


    def updateMany(self, query, updateExpression):
        query = self.__convertToObjectId(query)
        old_result = self.findMany(query)
        result = self.db[self.table].update_many(query, updateExpression)
        
        if not result.acknowledged:
            return False
        # TODO return the objects .find({'_id': { '$in': keys }})
        return [r['id'] for r in old_result]
    
    def findManyByIds(self, ids):
        query={
            "_id": {
                "$in": ids
            }
        }

        return self.findMany(query)

        
    def deleteMany(self, query):
        oldRecords = list(self.findMany(query))

        result = self.db[self.table].delete_many(self.__convertToObjectId(query))
        if not result.acknowledged:
            return False

        if not oldRecords:
            return [] 
        if len(oldRecords) == result.deleted_count:
            return oldRecords
        return False

    def __indexHash(self, indexDict):
        if indexDict and isinstance(indexDict, dict):
            return hashlib.md5(str({key:indexDict[key] for key in sorted(indexDict)}).encode()).hexdigest()
        return False


    def check_for_or_create_index(self, indexDict, name=None,unique=False):
        """Returns True if an index was added"""
        index = []
        # Sort and hash the dictionary to get a unique name as a string
        name = name if name else hashlib.md5(str({key:indexDict[key] for key in sorted(indexDict)}).encode()).hexdigest()
        # Make sure collect exist 
        try:
            self.db.create_collection(self.table, check_exists=True)
        except CollectionInvalid as e:
            pass

        # convert to python format 
        for k,v in indexDict.items():
            index.append((k,v))
        
        
        for i in self.db[self.table].list_indexes():
            if i['name'] == name:
                return False

        self.db[self.table].create_index(index, name=name,unique=unique)

        return True
        
    def dropIndex(self, index):
        """Returns True if an index was added"""
        if self.table not in self.db.list_collection_names():
             self.db.create_collection(self.table, check_exists=True)
        
        # print(name, index)
        for i in self.db[self.table].list_indexes():
            if i['name'] == index:
                self.db[self.table].drop_index(index)

        self.db[self.table].delete_one({'_id':'~~~~~~placeholder~~~~~'})


class BaseModel(MongoWrapper):

    def __init__(self, table, host = None) -> None:
        super().__init__(table=table, host=host)
        pass

class PermissionsBaseModel(MongoWrapper):

    def __init__(self, table, host = None) -> None:
        super().__init__(table=table, host=host)
        self.permissions_table_name = table+'_permissions'
        self.permissions = BaseModel(self.permissions_table_name, host=host)
        self.permissions.collection_indexes = [
            {
                "index":{'objectId':1, "userId":1},
                "options": {"unique":True}
            },
            {
                "index":{'objectId':1},
                "options":{"unique":False}
            },
            {
                "index":{"userId":1},
                "options":{"unique":False}
            }
        ]
        # self.permissions.check_for_or_create_index({'objectId':1,'userId':1}, unique=True)
        # self.permissions.check_for_or_create_index({'objectId':1}, unique=False)
        # self.permissions.check_for_or_create_index({'userId':1}, unique=False)
        # self.permissions.check_for_or_create_index({'object_id':1,'user_id':1}, unique=True)
        # self.permissions.check_for_or_create_index({'object_id':1}, unique=False)
        # self.permissions.check_for_or_create_index({'user_id':1}, unique=False)
        pass
        
    def updateIndexes(self):
        self.permissions.updateIndexes()
        return super().updateIndexes()

    def getAllPermissions(self,objectId):
        return self.permissions.findMany({'objectId':objectId})

    def getAllUserPermissions(self,userId):
        return self.permissions.findMany({'userId':userId})

    def getPermission(self, userId, objectId):
        return self.permissions.find({'objectId':objectId, 'userId':userId})

    def deletePermission(self, userId, objectId):
        perm = self.getPermission(userId, objectId)
        if perm:
            return self.permissions.delete(perm['id'])
        return False

    def setPermission(self, userId, objectId, data={}):
        perm = self.getPermission(userId, objectId)
        data['objectId'] = objectId
        data['userId'] = userId
        
        if 'type' not in data:
            data['type']=None
        
        if perm:
            perm.update(data)
            return self.permissions.replace(perm['id'],perm)

        return self.permissions.create(data)

    def getPermissionByType(self,objectId, type):
        return self.permissions.findMany({'objectId':objectId, 'type':type})

    # @property
    # def permissions(self)->BaseModel:
    #     return self.permissions
    


if __name__ == "__main__":
    pass