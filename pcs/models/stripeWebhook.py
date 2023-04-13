from pcs.models.baseModel import BaseModel


class StripeWebhook(BaseModel):

    def __init__(self) -> None:

        super().__init__("stripe-webhook-table")

