from pcs.models.baseModel import BaseModel

class User(BaseModel):

    def __init__(self) -> None:

        super().__init__("user-table")
        #Must come after init or ELSE!!!

