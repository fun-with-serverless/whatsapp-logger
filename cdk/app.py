#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.whatsapp_listener_stack import WhatsAppListener
from cdk.googlesheets_recorder_stack import GoogleSheetsRecorder
from cdk.qr_viewer import QRViewer
from cdk.shared_s3_bucket import SharedS3Bucket

app = cdk.App()
stage = app.node.try_get_context("stage") or "dev"
googlesheets_recorder = GoogleSheetsRecorder(app, f"GoogleSheetRecorder-{stage}")
shared_s3_bucket = SharedS3Bucket(app, f"SharedS3Bucket-{stage}")
qr_viewer = QRViewer(app, f"QrReader-{stage}", qr_bucket=shared_s3_bucket.qr_s3_bucket)
whatsapp_listener = WhatsAppListener(
    app,
    f"WhatsAppWebListener-{stage}",
    whatsapp_messages=googlesheets_recorder.whatsapp_message_sns,
    qr_bucket=shared_s3_bucket.qr_s3_bucket,
    lambda_url=qr_viewer.lambda_url,
)

app.synth()
