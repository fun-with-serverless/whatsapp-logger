#!/usr/bin/env python3
import os
import aws_cdk as cdk
from backend.iac.component import Backend
from whatsapp_web_listener.iac.component import WhatsAppListener

app = cdk.App()
env = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]
)
stage = os.environ.get("USER", "dev")
backend = Backend(app, f"Backend-{stage}", env=env)
WhatsAppListener(
    app,
    f"Client-{stage}",
    backend.whatsapp_message_sns,
    backend.qr_bucket,
    backend.event_bus,
    env=env,
)
app.synth()
