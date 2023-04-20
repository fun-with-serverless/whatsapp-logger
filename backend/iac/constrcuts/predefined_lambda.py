from typing import Optional
from constructs import Construct

from aws_cdk import (
    aws_lambda_python_alpha as lambda_python,
    aws_lambda,
)


class PythonLambda(lambda_python.PythonFunction):
    """
    A custom AWS CDK construct for creating Lambda functions written in Python.

    This class extends the `lambda_python.PythonFunction` class from the `aws_cdk` library
    and provides a simplified interface for creating Lambda functions.

    Args:
        scope (Construct): The parent construct of this construct.
        construct_id (str): The ID of this construct.
        runtime (_lambda.Runtime, optional): The version of Python to use for the Lambda function.
            Defaults to aws_lambda.Runtime.PYTHON_3_10.
        **kwargs: Additional keyword arguments that are passed to the `lambda_python.PythonFunction`
            constructor, such as `code`, `handler`, and `timeout`.

    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        runtime: Optional[aws_lambda.Runtime] = None,
        **kwargs,
    ) -> None:
        runtime = runtime or aws_lambda.Runtime.PYTHON_3_10
        super().__init__(scope, construct_id, runtime=runtime, **kwargs)
