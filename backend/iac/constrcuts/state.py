from constructs import Construct
from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
)


class State(Construct):
    @property
    def state_table(self) -> dynamodb.Table:
        return self._application_state_table

    @property
    def whatsapp_groups_table(self) -> dynamodb.Table:
        return self._whatsapp_groups_table

    @property
    def qr_bucket(self) -> s3.Bucket:
        return self._bucket

    @property
    def chats_lake(self) -> s3.Bucket:
        return self._chats_lake

    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self._application_state_table = dynamodb.Table(
            self,
            "ApplicationState",
            partition_key=dynamodb.Attribute(
                name="key", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        self._whatsapp_groups_table = dynamodb.Table(
            self,
            "WhatsAppGroups",
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        self._bucket = s3.Bucket(self, "QRImage")
        self._chats_lake = s3.Bucket(self, "ChatsLake")
