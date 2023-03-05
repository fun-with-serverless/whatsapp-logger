from __future__ import annotations
from datetime import datetime
import functools
import os
from typing import TYPE_CHECKING
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from ...utils.consts import SUMMARY_PREFIX

if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import S3ServiceResource, Bucket

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def handler(event, context: LambdaContext):

    s3 = _get_s3()
    bucket = s3.Bucket(os.environ["CHATS_BUCKET"])
    _move_files(
        bucket, s3, f"buckup/{datetime.now().strftime('%Y.%m.%d')}/{SUMMARY_PREFIX}"
    )


@functools.cache
def _get_s3() -> S3ServiceResource:
    return boto3.resource("s3")


def _move_files(
    bucket: Bucket,
    s3: S3ServiceResource,
    dest_prefix: str,
    src_prefix: str = SUMMARY_PREFIX,
):

    objects_to_move = bucket.objects.filter(Prefix=src_prefix)
    for obj in objects_to_move:
        old_key = obj.key
        new_key = old_key.replace(src_prefix, dest_prefix, 1)
        s3.Object(bucket.name, new_key).copy_from(CopySource=f"{bucket.name}/{old_key}")
        obj.delete()
