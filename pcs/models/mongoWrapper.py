import os
import boto3
import copy
import urllib.parse
import json
import time
import uuid
import hashlib
# importing ObjectId from bson library
from bson.objectid import ObjectId
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import CollectionInvalid
from pcs.util import secrets
from datetime import datetime


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

    def __init__(self, host, table, pemFilePath=None, db_name='main-mongo-database') -> None:
        self.table = table
        self.collection_indexes = []
        if pemFilePath:
            client = MongoClient(host,
                                    tls=True,
                                    tlsCAFile=pemFilePath)
        else:
            client = MongoClient(host, 27017)

        self.db = client[db_name]
        

    def updateIndexes(self):
        indexes = self.db[self.table].list_indexes()
        index_name_list = []
        collection_hash_list = []
        for i in indexes:
            index_name_list.append(i['name'])

        # Check in collection_indexes are in the indexes of the table. If not then add them.
        for col_index in self.collection_indexes:
            index = []
            for k, v in col_index['index'].items():
                index.append((k, v))
            name = self.__indexHash(col_index['index'])
            collection_hash_list.append(name)
            if name not in index_name_list:
                self.db[self.table].create_index(
                    index, name=name,  **col_index['options'])

        indexes = self.db[self.table].list_indexes()

        # Check if all the indexes of the table are in the collection index. If not then delete it.
        for i in indexes:
            if i['name'] != "_id_" and i['name'] not in collection_hash_list:
                self.db[self.table].drop_index(i)

    def setCreated(self, item):
        if "created" not in item:
            item['created'] = datetime.now()
        
        return item
    
    def setModified(self, item, override=True):
        if override:
            item['modified'] = datetime.now()
        
        #Override is false and modified is not in the item
        if not override and "modified" not in item:
            item['modified'] = datetime.now()

        return item

    def __toDBID(self, val):
        try:
            return str(ObjectId(str(val)))
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

        # If an object doesn't have an ID
        if '_id' not in obj:
            obj['_id'] = str(uuid.uuid4())
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
            return self.replace(obj['id'], item)

        return False

    def put(self, item, projection=False):
        newItem = copy.deepcopy(item)
        newItem = self.setCreated(newItem)
        newItem = self.setModified(newItem)
        # To go from python to low-level format
        result = self.db[self.table].insert_one(
            self.__convertToObjectId(newItem))
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
        if not result:
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
        newItem = self.setModified(newItem)
        result = self.db[self.table].replace_one({
            '_id': self.__toDBID(itemId)
        }, self.__convertToObjectId(newItem))

        if not result.acknowledged:
            return False

        return self.get(itemId, projection)

    def update(self, itemId, updateExpression):
        result = self.db[self.table].update_one({
            '_id': self.__toDBID(itemId)
        }, updateExpression)
        if not result.acknowledged:
            return False
        
        #if update doesn't fail then create new updateExpression and update modified
        timeUpdateExp = {
            "$set" : {
                "modified" : datetime.now()
            }
        }
        result = self.db[self.table].update_one({
                '_id': self.__toDBID(itemId)
            }, timeUpdateExp)
        
        if not result.acknowledged:
            return False

        return self.get(itemId)

    def putMany(self, items, projection=False):
        converted = []
        for item in list(items):
            item = self.setCreated(item)
            item = self.setModified(item)
            converted.append(self.__convertToObjectId(item))
        # insert many objects to collection
        result = self.db[self.table].insert_many(converted)

        if not result.acknowledged:
            return False

        return [str(obj_id) for obj_id in result.inserted_ids]

    def insertMany(self, items, projection=False):
        return self.putMany(items, projection)

        # Just an Alias for getItems
    def findMany(self, query, projection=False, limit=0, skip=False):
        """
        Alias for getItems
        """
        return self.getMany(query, projection=projection, limit=limit, skip=skip)

    def getMany(self, query, projection=False, limit=0, skip=False):
        # result = self.db[self.table].find(self.__convertToObjectId(query)).limit(limit)
        result = self.db[self.table].find(query).limit(limit)

        if skip != False:
            result.skip(skip)

        if not result:
            return result

        converted = []
        for item in list(result):
            converted.append(self.__convertToId(item))

        return converted

 
    #Needed to add update to modified for this one
    def find_one_and_update(self, query, updateExpression):
    
        result = self.db[self.table].find_one_and_update(query, updateExpression, return_document=ReturnDocument.AFTER)
        
        itemId = result["_id"]

        #Allows modified to get updated
        timeUpdateExp = {
            "$set" : {
                "modified" : datetime.now()
            }
        }

        result = self.db[self.table].update_one({
                '_id': self.__toDBID(itemId)
            }, timeUpdateExp)
        
        if not result.acknowledged:
            return False

        return self.get(itemId)


    def updateMany(self, query, updateExpression):
        query = self.__convertToObjectId(query)
        old_result = self.findMany(query)
        result = self.db[self.table].update_many(query, updateExpression)

        if not result.acknowledged:
            return False
        
        timeUpdateExp = {
            "$set" : {
                "modified" : datetime.now()
            }
        }
        result = self.db[self.table].update_many(query, timeUpdateExp)
        
        if not result.acknowledged:
            return False
        # TODO return the objects .find({'_id': { '$in': keys }})
        return [r['id'] for r in old_result]

    def findManyByIds(self, ids):
        query = {
            "_id": {
                "$in": ids
            }
        }

        return self.findMany(query)

    def deleteMany(self, query):
        oldRecords = list(self.findMany(query))

        # result = self.db[self.table].delete_many(self.__convertToObjectId(query))
        result = self.db[self.table].delete_many(query)
        if not result.acknowledged:
            return False

        if not oldRecords:
            return []
        if len(oldRecords) == result.deleted_count:
            return oldRecords
        return False
    
    # TODO: Create aggregate for permission based models
    """
    base_key = column for MongoWrapper
    perm_key = column for PermissionsModel
    query
    perm_model = Used to get permissions
    """

    def aggregate(self, query, model: "MongoWrapper", base_key, perm_key, convertIds=True):

        result = self.db[self.table].aggregate([
            {
                "$match": query,
            },
            {
                "$lookup":  # This will be our join function
                {
                    "from": model.table,  # <collection to join>,
                    "localField": base_key,  # <field from the input documents>
                    "foreignField": perm_key,  # <field from the documents of the "from" collection>,
                    "as": model.table # <output array field> Ex. "file and file-permissions"
                }
            }
        ])
        
        if not convertIds:
            return result
        
        result = list(result)

        for r in result:
            r = self.__convertToId(r)
            for m in r[model.table]:
                m = self.__convertToId(m)

        return result

    def __indexHash(self, indexDict):
        if indexDict and isinstance(indexDict, dict):
            return hashlib.md5(str({key: indexDict[key] for key in sorted(indexDict)}).encode()).hexdigest()
        return False

    def check_for_or_create_index(self, indexDict, name=None, unique=False):
        """Returns True if an index was added"""
        index = []
        # Sort and hash the dictionary to get a unique name as a string
        name = name if name else hashlib.md5(
            str({key: indexDict[key] for key in sorted(indexDict)}).encode()).hexdigest()
        # Make sure collect exist
        try:
            self.db.create_collection(self.table, check_exists=True)
        except CollectionInvalid as e:
            pass

        # convert to python format
        for k, v in indexDict.items():
            index.append((k, v))

        for i in self.db[self.table].list_indexes():
            if i['name'] == name:
                return False

        self.db[self.table].create_index(index, name=name, unique=unique)

        return True

    def dropIndex(self, index):
        """Returns True if an index was added"""
        if self.table not in self.db.list_collection_names():
            self.db.create_collection(self.table, check_exists=True)

        # print(name, index)
        for i in self.db[self.table].list_indexes():
            if i['name'] == index:
                self.db[self.table].drop_index(index)

        self.db[self.table].delete_one({'_id': '~~~~~~placeholder~~~~~'})


if __name__ == "__main__":
    pass
