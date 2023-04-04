import os
import json
import types
import inspect
from pcs.controllers import baseController

#TODO: Make backwards compatible with old controllers

class GQLServerlessApp():
    def __init__(self, userId=None, username=None, payload=None, source=None):
        self.userId = userId
        self.username = username
        self.payload = payload
        self.source = source
        self.gqlMap = {}


    def linkGraphQL(self, controllerClass, parentType=None, action=None, func=None, kwargs=None, args=None):
        if parentType not in self.gqlMap:
            self.gqlMap[parentType] = []
        
        if not inspect.isclass(controllerClass) and not isinstance(controllerClass, baseController.BaseController):
            raise Exception("Controller must be a Class or Instance that extends BaseController!!!!")

        controller_map = {
            "class":controllerClass, #can be instance or class
            # "instance":None,
            "action":None,
            "func":None,
            "kwargs": kwargs,
            "args": args,
            }
        
        #If action or func are specified
        if action or func:
            #Make sure action and func are Strings respectively
            if not (isinstance(action, str) and isinstance(func, str)):
                # If not exception or only 1 of them was specified
                raise Exception("Action and Function must be specified together as a String and Function!!!!")
            
            #if both are specified and are the correct type add them to the controller_map
            controller_map['action'] = action
            controller_map['func'] = func

        self.gqlMap[parentType].append(controller_map)
    

    def run(self, parentType, action):
        controllers = self.gqlMap.get(None, [])
        
        # Check to see if parentType is in self.gqlMap
        # if parentType in the map
        if parentType in self.gqlMap:
            controllers = self.gqlMap[parentType]
        
        # if class then convert it to instance after if statement

        #for each loop for this
        for control in controllers:
            cls = control.get("class")
            kwargs = control.get("kwargs")
            args = control.get("args")
            if not cls:
                continue
                
            func_name = action
            if control.get("action") == action:
                func_name = control.get("func")
            
            fn = getattr(cls, func_name, None)

            if not fn:
                continue
            
            if inspect.isclass(cls):
                cls = cls(userId=self.userId, username=self.username, payload=self.payload, source=self.source)
                fn = getattr(cls, func_name, None)

            if kwargs and args:
                return fn(*args, **kwargs)
            elif kwargs:
                return fn(**kwargs)
            elif args:
                return fn(*args)
            return fn()