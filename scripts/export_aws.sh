#!/bin/bash

# Extract the credentials from the file
access_key=$(grep aws_access_key_id ~/.aws/credentials | awk -F " = " '{print $2}')
secret_key=$(grep aws_secret_access_key ~/.aws/credentials | awk -F " = " '{print $2}')

# Set the environment variables
export AWS_ACCESS_KEY_ID=$access_key
export AWS_SECRET_ACCESS_KEY=$secret_key