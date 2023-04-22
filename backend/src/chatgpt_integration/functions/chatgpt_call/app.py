from __future__ import annotations
from dataclasses import asdict
import functools
import json
import os
from typing import TYPE_CHECKING, Callable
import boto3
import openai
import tiktoken
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities import parameters

from ....utils.db_models.whatsapp_groups import SummaryLanguage, WhatsAppGroup

from ...utils.models import ChatGPTSummary

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
    language = SummaryLanguage.ENGLISH.value
    try:
        language = WhatsAppGroup.get(summary["group_id"]).summary_language.value
    except WhatsAppGroup.DoesNotExist:
        logger.info("Missing group id. Using default.", group_id=summary["group_id"])
    content = _get_valid_content(summary["chats"], language)
    response = chatgpt.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a stenographer",
            },
            {
                "role": "user",
                "content": content,
            },
        ],
    )
    logger.info(
        "ChatGPT summary",
        query_sent=content,
        gpt_reponse=response["choices"][0]["message"]["content"],
        gorup_name=summary["group_name"],
    )
    return asdict(
        ChatGPTSummary(
            content=response["choices"][0]["message"]["content"],
            group_name=summary["group_name"],
            group_id=summary["group_id"],
        )
    )


@functools.cache
def _get_s3() -> S3ServiceResource:
    return boto3.resource("s3")


@functools.cache
def _get_openai():
    return openai


@functools.cache
def _get_encoding():
    return tiktoken.encoding_for_model("gpt-3.5-turbo")


def _get_valid_content(content: str, language: str):
    string_template = "The text is a conversation in a forum where people are discussing various topics. Summerize the following text by dividing into topics: {}. Write your answers in {}"
    encoding = _get_encoding()
    found_string = _find_max_substring(
        content=content, token_function=lambda val: len(encoding.encode(val))
    )
    return string_template.format(found_string, language)


def _find_max_substring(
    content: str, token_function: Callable[[str], int], max_tokens: int = 4000
):
    """

    This function finds the longest substring that starts from the beginning of the input string content and
    satisfies the constraint that the number of tokens (determined by token_function) is not greater than max_tokens.

    Args:
    content (str): The input string from which the longest substring is to be found.
    token_function (callable): A function that takes a string as input and returns the number of tokens in the string.
    max_tokens (int, optional): The maximum number of tokens allowed in the substring. Default is 4000.

    Returns:
    str: The longest substring that starts from the beginning of the input string and has no more than max_tokens tokens.
    """
    left, right = 0, len(content)

    while left < right:
        mid = (left + right) // 2
        substring = content[0 : mid + 1]
        magic_value = token_function(substring)

        if magic_value <= max_tokens:
            left = mid + 1
        else:
            right = mid

    # Here is the maximal index value for the substring that starts with the first element and meets the requirement
    max_index = left - 1
    return content[0 : max_index + 1]
