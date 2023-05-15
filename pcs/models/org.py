from pcs.models.mongoWrapper import MongoWrapper, PermissionsModel

#Take this out of the framework
class OrgPermissions(PermissionsModel):
    def __init__(self)-> None:
        super().__init__("org-table")
    
class OrgFile(MongoWrapper):
    def __init__(self)-> None:
        self.permissions = OrgFilePermissions()
        super().__init__("org-file-table")

class OrgFilePermissions(PermissionsModel):
    def __init__(self)-> None:
        super().__init__("org-file-table-permissions")


#Associate files with objects or by themselves
class Organization(MongoWrapper):
    def __init__(self) -> None:
        self.permissions = OrgPermissions() #Associate with OrgPermissions
        self.files = OrgFile() #Associate with OrgFile
        super().__init__("organization-table")
    
    #TODO: Match files to permissions
    def getImages(self, orgId):
        query = {
            "org": orgId
        }
        result = self.files.aggregate(query, self.files.permissions, "org", "userId")
        # img_list = self.files.findMany({
        #     "org": orgId
        # })
        # self.files.permissions.getAllPermissions(orgId)
        result = list(result)

        if not result:
            return []
        return result
        

    def getImagePermissions(self, orgId):
        pass
    
    def addImage(self, orgId):
        image = {}
        image['org'] = orgId
        image = self.files.create(image)
        self.files.permissions.setPermission(orgId, image['id'])
        return image


# Example use of Organization
# org.files.permissions.setPermission() OrgFile Permission setting
# org.files.create() File creation
# org.permissions.setPermission() Organization Permissions

