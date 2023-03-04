from __future__ import annotations
import functools
import json
import os
from typing import TYPE_CHECKING
import boto3
import openai
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities import parameters

if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import S3ServiceResource

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def handler(event, context: LambdaContext):
    chatgpt = _get_openai()
    chatgpt.api_key = str(parameters.get_secret(os.environ["OPENAI_KEY"]))
    s3 = _get_s3()
    content = (
        s3.Object(
            os.environ["CHATS_BUCKET"],
            event["file_name"],
        )
        .get()["Body"]
        .read()
        .decode("utf-8")
    )
    summary = json.loads(content)
    response = chatgpt.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"The text is a conversation in a forum where people are discussing various topics. Summerize the following text {summary['chats'][:3940]} Divide the summery into the different topics",
            },
        ],
    )
    logger.info(
        "ChatGPT summary", gpt_reponse=response["choices"][0]["message"]["content"]
    )
    return {
        "content": response["choices"][0]["message"]["content"],
        "group_name": summary["group_name"],
        "group_id": summary["group_id"],
    }


@functools.cache
def _get_s3() -> S3ServiceResource:
    return boto3.resource("s3")


@functools.cache
def _get_openai():
    return openai
