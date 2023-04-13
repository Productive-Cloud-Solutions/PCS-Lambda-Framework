from pcs.models.baseModel import BaseModel



class Record(BaseModel):

    def __init__(self) -> None:

        super().__init__("record-table")
        #Must come after init or ELSE!!!

