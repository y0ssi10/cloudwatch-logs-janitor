# CloudWatch Logs Janitor

## Features

- Set the retention periods of new CloudWatch log groups to the numbers of days you set up.
- Set the retention periods of existing CloudWatch log groups which is never expire to the numbers of days you set up.
- Delete all CloudWatch log groups for API Gateway Log Events and AWS Lambda.

## Packages

```bash
.
├── README.md                   <-- This instructions file
├── cloudwatch_logs_janitor     <-- Source code for a lambda function
│   ├── __init__.py
│   ├── janitor.py              <-- Lambda function code
├── template.yaml               <-- SAM Template
|── Pipfile                     <-- Python dependencies
└── tests                       <-- Unit tests
    └── unit
        ├── __init__.py
        └── test_handler.py
```

### Requirements

- AWS CLI already configured with Administrator permission
- [Python 3 installed](https://www.python.org/downloads/)
- [Pipenv installed](https://docs.pipenv.org/en/latest/)
- [Docker installed](https://www.docker.com/community-edition)

## Appendix

### SAM and AWS CLI commands

Commands to package, deploy resources within CloudFormation template:

```bash
# Package Lambda function defined locally and upload to S3 as an artifact
sam package \
    --output-template-file packaged.yaml \
    --s3-bucket REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME

# Deploy SAM template as a CloudFormation stack
sam deploy \
    --template-file packaged.yaml \
    --stack-name sam-app \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides LogGroupRetention=REPLACE_THIS_WITH_YOUR_SETTING_VALUE
```

## Licensing

MIT License (MIT)

This software is released under the MIT License, see LICENSE.
