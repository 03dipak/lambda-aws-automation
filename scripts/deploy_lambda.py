"""
repo-root/
├── lambdas/
│   ├── lambda1/
│   │   ├── lambda_function.py
│   │   └── requirements.txt (optional)
│   ├── lambda2/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   └── ...
├── .github/
│   └── workflows/
│       └── deploy-lambdas.yml
└── scripts/
    └── deploy_lambda.py

"""
#scripts/deploy_lambda.py

import boto3
import zipfile
import os
import sys

def zip_lambda(lambda_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(lambda_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, lambda_path)
                zipf.write(file_path, arcname)

def deploy_lambda(lambda_name, lambda_path, role_arn, region, runtime="python3.10", handler="lambda_function.lambda_handler"):
    zip_path = f"/tmp/{lambda_name}.zip"
    zip_lambda(lambda_path, zip_path)

    client = boto3.client('lambda', region_name=region)
    with open(zip_path, 'rb') as f:
        zipped_code = f.read()

    try:
        client.get_function(FunctionName=lambda_name)
        print(f"Updating Lambda: {lambda_name}")
        response = client.update_function_code(
            FunctionName=lambda_name,
            ZipFile=zipped_code,
            Publish=True
        )
    except client.exceptions.ResourceNotFoundException:
        print(f"Creating Lambda: {lambda_name}")
        response = client.create_function(
            FunctionName=lambda_name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': zipped_code},
            Timeout=30,
            Publish=True
        )

    print(response)

if __name__ == "__main__":
    lambda_name = sys.argv[1]
    lambda_path = sys.argv[2]
    role_arn = sys.argv[3]
    region = sys.argv[4]
    deploy_lambda(lambda_name, lambda_path, role_arn, region)
