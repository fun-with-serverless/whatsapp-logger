#!/usr/bin/env python3

import aws_cdk as cdk

from cdk.whatsapp_listener_stack import WhatsAppListener
from cdk.googlesheets_recorder_stack import GoogleSheetsRecorder
from cdk.admin_panel import AdminPanel
from cdk.configuration import Configuration
from cdk.shared_s3_bucket import SharedS3Bucket

app = cdk.App()
stage = app.node.try_get_context("stage") or "dev"
configuration = Configuration(app, f"Configuration-{stage}")
googlesheets_recorder = GoogleSheetsRecorder(
    app, f"GoogleSheetRecorder-{stage}", configuration=configuration
)
shared_s3_bucket = SharedS3Bucket(app, f"SharedS3Bucket-{stage}")
admin_panel = AdminPanel(
    app,
    f"QrReader-{stage}",
    qr_bucket=shared_s3_bucket.qr_s3_bucket,
    configuration=configuration,
)
whatsapp_listener = WhatsAppListener(
    app,
    f"WhatsAppWebListener-{stage}",
    whatsapp_messages=googlesheets_recorder.whatsapp_message_sns,
    qr_bucket=shared_s3_bucket.qr_s3_bucket,
    lambda_url=admin_panel.lambda_url,
)

app.synth()
