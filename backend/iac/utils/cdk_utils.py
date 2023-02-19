import os
import subprocess

from aws_cdk import (
    aws_lambda_python_alpha as lambda_python,
    aws_lambda as _lambda,
    Stack,
)


def prepare_layer(
    stack: Stack, layer_name: str, poetry_dir: str, req_dir: str = ".build/common_layer"
) -> lambda_python.PythonLayerVersion:
    """
    This method is used to prepare a layer for AWS Lambda, by generating a
    requirements file for the dependencies of the project
    and creating a lambda_python.PythonLayerVersion object for the layer.

    stack: a Stack object
    layer_name: a string representing the name of the layer
    poetry_dir: a string representing the path of the directory containing
    poetry projects.
    req_dir: a string representing the path of the directory to store the
    generated requirements file. The default value is ".build/common_layer".
    """
    path = f"{req_dir}_{stack.stack_name}"
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

    result = subprocess.run(
        f"poetry export --directory={poetry_dir} --without=dev --with=layer --without-hashes > {path}/requirements.txt",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise Exception(f"Poetry command failed with error: {result.stderr.decode()}")

    return lambda_python.PythonLayerVersion(
        stack,
        layer_name,
        entry=path,
        compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
    )
