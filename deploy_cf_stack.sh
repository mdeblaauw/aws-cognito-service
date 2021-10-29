#!/bin/bash

Stage="$1" # dev, test, or prod

Region="eu-west-1"
ApplicationName="cognito-authentication"
StackName="${ApplicationName}-${Stage}"

# Remove lambda_layer folder if exist
if [ lambda_layer/ ]; then
    rm -rf lambda_layer/
fi

# Create lambda_layer folder and copy lambda_layer content to it

echo "Make local lambda layer folder"

mkdir -p lambda_layer/python/

rm -rf lambda_utils/lambda_utils/__pycache__
cp -r lambda_utils/lambda_utils lambda_layer/python/

# Run Cloudformation stack for S3 bucket

echo "Deploy S3 Cloudformation deployment bucket"

aws cloudformation deploy \
    --region $Region \
    --template-file "./cf_stacks/cf_s3_upload_stack.yaml" \
    --stack-name "${ApplicationName}-s3-cf-deployment-${Stage}" \
    --parameter-overrides \
        ProductionStage=$Stage \
        ApplicationName=$ApplicationName \
    --capabilities "CAPABILITY_IAM"

S3DeploymentBucket=$(aws cloudformation list-exports \
    --region $Region \
    --query "Exports[?Name==\`${ApplicationName}-cf-bucket-${Stage}\`].Value" \
    --output text)

# Run main Cloudformation stack

echo 'Deploy main stack'

# aws cloudformation package \
#     --region $Region \
#     --template-file "./cf_stacks/apig_lambdas/cf_apig_lambdas_stack.yaml" \
#     --s3-bucket $S3DeploymentBucket \
#     --output-template-file "./cf_stacks/apig_lambdas/cf_apig_lambdas_stack.packaged.yaml" \

# aws cloudformation deploy \
#     --region $Region \
#     --template-file "./cf_stacks/apig_lambdas/cf_apig_lambdas_stack.packaged.yaml" \
#     --stack-name $StackName \
#     --parameter-overrides \
#         ProductionStage=$Stage \
#         ApplicationName=$ApplicationName \
#     --capabilities "CAPABILITY_IAM"

aws cloudformation package \
    --region $Region \
    --template-file "./cf_stacks/cf_api_gateway_stack.yaml" \
    --s3-bucket $S3DeploymentBucket \
    --output-template-file "./cf_stacks/cf_api_gateway_stack.packaged.yaml" \

aws cloudformation deploy \
    --region $Region \
    --template-file "./cf_stacks/cf_api_gateway_stack.packaged.yaml" \
    --stack-name $StackName \
    --parameter-overrides \
        ProductionStage=$Stage \
        ApplicationName=$ApplicationName \
    --capabilities "CAPABILITY_IAM"