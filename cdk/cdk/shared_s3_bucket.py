from aws_cdk import (
    Stack,
    aws_s3 as s3,
)
from constructs import Construct


class SharedS3Bucket(Stack):
    @property
    def qr_s3_bucket(self) -> s3.Bucket:
        return self._bucket

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._bucket = s3.Bucket(self, "QRImage")
