#!/usr/bin/env python3
import os
import aws_cdk as cdk
import component  # type: ignore


app = cdk.App()
env = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]
)
stage = os.environ.get("USER", "dev")
component.StaticWeb(
    app,
    f"WebSite-{stage}",
    env=env,
)

app.synth()
