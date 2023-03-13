from aws_cdk import aws_s3_deployment as s3deploy
import shutil
import os
from constructs import Construct
import boto3
from urllib.parse import urlparse


from aws_cdk import Stack, aws_s3 as s3, Fn, aws_cloudfront as cloudfront

# It's ugly and I hate it.
# See https://github.com/aws/aws-cdk/issues/17475
def get_cf_output(export_name):
    cloudformation = boto3.client("cloudformation")
    response = cloudformation.list_exports()

    for export in response["Exports"]:
        if export["Name"] == export_name:
            return export["Value"]

    raise ValueError(f"Export {export_name} not found")


class StaticWeb(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        suffix = os.environ.get("USER", "NoUser")
        domain = get_cf_output(f"BackendURL-{suffix}")

        destination_bucket = s3.Bucket.from_bucket_arn(
            self,
            "DestinationBucket",
            bucket_arn=Fn.import_value(f"WebBucketArn-{suffix}"),
        )
        distribution = cloudfront.Distribution.from_distribution_attributes(
            self,
            "Distribution",
            distribution_id=Fn.import_value(f"DashboardDistributionId-{suffix}"),
            domain_name=urlparse(domain).netloc,
        )

        static_source = self._create_static_content(domain, suffix)
        s3deploy.BucketDeployment(
            self,
            "DeployWebsite",
            sources=[s3deploy.Source.asset(static_source)],
            destination_bucket=destination_bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

    def _create_static_content(self, domain: str, suffix: str) -> str:
        build_path = "../../.build"
        destination = f"{build_path}/static_web-{suffix}"

        if os.path.exists(destination):
            shutil.rmtree(destination)

        shutil.copytree("../src", destination)

        with open(f"{destination}/script.js", "r") as file:
            # read the file content
            file_content = file.read()
        new_content = file_content.replace("$URL$", domain)

        with open(f"{destination}/script.js", "w") as file:
            # write the modified content to the file
            file.write(new_content)

        return destination
