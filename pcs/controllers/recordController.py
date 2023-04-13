import os
import json
# from models import user_old as user_model
from pcs.models.record import Record
from pcs.models.user import User
from datetime import datetime
from pcs.controllers.baseController import BaseController

record_model= Record()
user_model= User()

class RecordController(BaseController):

    def getRecord(self):
        if not self.userId:
            raise Exception("User was not found")
        if not self.payload.get("recordId"):
            raise Exception("Record was not found")
        
        user= user_model.get(self.userId) 
        if not user:
            raise Exception("User was not found!!!")
        
        query= {
            'userId': self.userId,
            '_id': self.payload['recordId'],
        }
        
        record = record_model.find(query)
        if not record:
            raise Exception("Failed to find record!!!")
        return record
    
    
    def getRecords(self):
        if not self.userId:
            raise Exception("User was not found")
        
        user= user_model.get(self.userId) 
        if not user:
            raise Exception("User was not found!!!")
        
        query= {
            'userId': self.userId,
        }
        
        records = record_model.findMany(query)
        if not records:
            return []
        return records

    def createRecord(self):
        if not self.userId:
            raise Exception("User was not found")
        if not self.payload.get("name"):
            raise Exception("Name cannot be empty!!!") 
        if not self.payload.get("description"):
            raise Exception("Description cannot be empty!!!") 
        if not self.payload.get("file"):
            raise Exception("File cannot be empty!!!") 
        
        user= user_model.get(self.userId) 
        if not user:
            raise Exception("User was not found!!!")
        
        self.payload['userId']=self.userId
        
        record = record_model.create(self.payload)
        if not record:
            raise Exception("Failed to create record!!!")
        
        return record

    def updateRecord(self):
        # record =record_model.get(self.payload['record_id'])

        if not self.userId:
            raise Exception("User was not found")
        if not self.payload.get("recordId"):
            raise Exception("Record was not found")

        user= user_model.get(self.userId) 
        if not user:
            raise Exception("User was not found!!!")
        
        # self.payload['userId']=self.userId
        
        query= {
            'userId': self.userId,
            '_id': self.payload['recordId'],
        }
        
        record = record_model.find(query)
        if not record:
            raise Exception("Failed to find record!!!")
        
        record.update(self.payload['record'])
        
        record= record_model.replace(record['id'],record)
        if not record:
            raise Exception("Failure to update")
          
        return record
    
    def deleteRecord(self):
        if not self.userId:
            raise Exception("User was not found")
        if not self.payload.get("recordId"):
            raise Exception("Record was not found")

        user= user_model.get(self.userId) 
        if not user:
            raise Exception("User was not found!!!")
        
        # self.payload['userId']=self.userId
        record = record_model.get(self.payload.get("recordId"))
        if record['userId'] != self.userId:
            raise Exception("Cannot delete record")
        
        record = record_model.delete(self.payload.get("recordId"))
        
        if not record:
            return True
        
        return record