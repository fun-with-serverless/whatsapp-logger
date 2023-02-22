from constructs import Construct
from aws_solutions_constructs.aws_cloudfront_s3 import CloudFrontToS3
from aws_cdk import aws_s3 as s3, CfnOutput


class Dashboard(Construct):
    @property
    def dashboard_domain(self) -> str:
        return self._domain

    @property
    def website_bucket(self) -> s3.IBucket:
        return self._ws_bucket

    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        cfs3 = CloudFrontToS3(self, "Dashboard", insert_http_security_headers=False)
        self._domain = cfs3.cloud_front_web_distribution.domain_name
        self._ws_bucket = cfs3.s3_bucket_interface

        CfnOutput(
            self,
            "WebBucketArn",
            export_name="WebBucketArn",
            value=cfs3.s3_bucket_interface.bucket_arn,
        )
