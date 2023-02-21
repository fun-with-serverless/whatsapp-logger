from aws_cdk import aws_s3_deployment as s3deploy
import shutil
import os
from constructs import Construct


from aws_cdk import Stack, aws_s3 as s3, Fn


class StaticWeb(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        domain: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        destination_bucket = s3.Bucket.from_bucket_arn(self, "DestinationBucket", bucket_arn=Fn.import_value("WebBucketArn"))
        static_source = self._create_static_content(domain)
        s3deploy.BucketDeployment(
            self,
            "DeployWebsite",
            sources=[s3deploy.Source.asset(static_source)],
            destination_bucket=destination_bucket,
        )

    def _create_static_content(self, domain: str) -> str:
        build_path = "../../.build"
        destination = f"{build_path}/static_web"

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
