#!/usr/bin/env python3
import os
import aws_cdk as cdk
import component  # type: ignore
import boto3

# It's ugly and I hate it.
# See https://github.com/aws/aws-cdk/issues/17475
def get_cf_output(export_name):
    cloudformation = boto3.client("cloudformation")
    response = cloudformation.list_exports()

    for export in response["Exports"]:
        if export["Name"] == export_name:
            return export["Value"]

    raise ValueError(f"Export {export_name} not found")


app = cdk.App()
env = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]
)
stage = os.environ.get("USER", "dev")
component.StaticWeb(
    app,
    f"WebSite-{stage}",
    env=env,
    domain=get_cf_output("BackendURL"),
)

app.synth()
