#!/usr/bin/env python3
import os
import aws_cdk as cdk

from cdk.whatsapp_listener_stack import WhatsAppListener
from cdk.googlesheets_recorder_stack import GoogleSheetsRecorder
from cdk.admin_panel import AdminPanel
from cdk.configuration import Configuration
from cdk.shared_s3_bucket import SharedS3Bucket
from cdk.event_bus import EventBus

app = cdk.App()
env = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]
)
stage = app.node.try_get_context("stage") or "dev"
event_bus = EventBus(app, f"EventBus-{stage}", env=env)
configuration = Configuration(app, f"Configuration-{stage}", env=env)
googlesheets_recorder = GoogleSheetsRecorder(
    app, f"GoogleSheetRecorder-{stage}", configuration=configuration, env=env
)
shared_s3_bucket = SharedS3Bucket(app, f"SharedS3Bucket-{stage}", env=env)
admin_panel = AdminPanel(
    app,
    f"QrReader-{stage}",
    qr_bucket=shared_s3_bucket.qr_s3_bucket,
    configuration=configuration,
    env=env,
    event_bus=event_bus.event_bus,
)
whatsapp_listener = WhatsAppListener(
    app,
    f"WhatsAppWebListener-{stage}",
    whatsapp_messages=googlesheets_recorder.whatsapp_message_sns,
    qr_bucket=shared_s3_bucket.qr_s3_bucket,
    lambda_url=admin_panel.lambda_url,
    env=env,
    event_bus=event_bus.event_bus,
)

app.synth()
