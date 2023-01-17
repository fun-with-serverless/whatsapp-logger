#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import CdkStack


app = cdk.App()
stage = app.node.try_get_context("stage") or "dev"
CdkStack(app, f"WhatsAppWebListener-{stage}")

app.synth()
