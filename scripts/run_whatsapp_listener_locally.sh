#!/bin/bash
set -e

# Used by whatsapp-web-listener project to run the container locally. Don't run this script directly, instead use "npm run run-local"
# Extract the credentials from the file
access_key=$(grep aws_access_key_id ~/.aws/credentials | awk -F " = " '{print $2}')
secret_key=$(grep aws_secret_access_key ~/.aws/credentials | awk -F " = " '{print $2}')

# Set the environment variables
AWS_ACCESS_KEY_ID=$access_key
AWS_SECRET_ACCESS_KEY=$secret_key

docker build -t whatsapp-web-listener whatsapp_web_listener/
docker run --env-file ./whatsapp_web_listener/.env -e AWS_REGION=us-east-1 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY  whatsapp-web-listener
