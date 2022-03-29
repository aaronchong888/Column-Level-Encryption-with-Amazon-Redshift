# Column-Level-Encryption-with-Amazon-Redshift

Implementing column-level encryption to protect PII data with Amazon Redshift

## Getting Started

### Prerequisites

- Python 3.7
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [pycryptodome](https://pycryptodome.readthedocs.io/en/latest/index.html)
- [miscreant](https://github.com/miscreant/meta)

Tested on **AWS Lambda** with the `Python 3.7` Runtime and **AWS Glue** with the `Glue 3.0` Runtime

### Usage

For **AWS Lambda**, create a .zip file deployment package with the required dependencies and upload it to AWS Lambda console.

1. Install the `miscreant` library to a new package directory

```
pip install --target ./package miscreant
```

2. Create a deployment package with the installed library at the root

```
cd package
zip -r ../my-deployment-package.zip .
```

3. Add the `aws_lambda_udf-redshift_encrypt-decrypt-logic.py` file to the root of the zip file

```
cd ..
zip -g my-deployment-package.zip aws_lambda_udf-redshift_encrypt-decrypt-logic.py
```

4. Create a new Lambda function with `Python 3.7` runtime, then [upload](https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-zip.html#configuration-function-update) the `my-deployment-package.zip` for the function code

For **AWS Glue**, copy and paste all the code within the `aws_glue_pyspark-encryption.py` file to replace the template script generated by the AWS Glue Studio.

- Under **Job Details**, expand the **Advanced properties** section and specify the **Job parameters** with Key `--additional-python-modules` and Value `miscreant`

## Authors

* **Aaron Chong** - *Initial work* - [aaronchong888](https://github.com/aaronchong888)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
