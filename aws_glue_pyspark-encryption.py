# import required libraries
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrameCollection
from awsglue.dynamicframe import DynamicFrame
import boto3
import base64
from miscreant.aes.siv import SIV
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType

# retrieve the data encryption key from Secrets Manager
secret_name = '<--ARN-OF-YOUR-SECRETS-MANAGER-SECRET-NAME-->'
sm_client = boto3.client('secretsmanager')
get_secret_value_response = sm_client.get_secret_value(SecretId = secret_name)
data_encryption_key = get_secret_value_response['SecretBinary']
siv = SIV(data_encryption_key)  # Without nonce, the encryption becomes deterministic

# define the data encryption function
def pii_encrypt(value):
    if value is None:
        value = ""
    ciphertext = siv.seal(value.encode())
    return base64.b64encode(ciphertext).decode('utf-8')

# register the data encryption function as Spark SQL UDF   
udf_pii_encrypt = udf(lambda z: pii_encrypt(z), StringType())

# define the Glue Custom Transform function
def Encrypt_PII (glueContext, dfc) -> DynamicFrameCollection:
    newdf = dfc.select(list(dfc.keys())[0]).toDF()
    # PII fields to be encrypted
    pii_col_list = ["cust_name", "day_of_birth", "email_addr"]

    for pii_col_name in pii_col_list:
        newdf = newdf.withColumn(pii_col_name, udf_pii_encrypt(col(pii_col_name)))

    newcustomerdyc = DynamicFrame.fromDF(newdf, glueContext, "newcustomerdata")
    return (DynamicFrameCollection({"CustomTransform0": newcustomerdyc}, glueContext))

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket with crawler
S3bucket_node1 = glueContext.create_dynamic_frame.from_catalog(
    database="<--AWS-GLUE-CATALOG-DATABASE-NAME-->",
    table_name="<--AWS-GLUE-CATALOG-TABLE-NAME-->",
    transformation_ctx="S3bucket_node1",
)

# Script generated for node ApplyMapping
ApplyMapping_node2 = ApplyMapping.apply(
    frame=S3bucket_node1,
    mappings=[
        ("col0", "string", "cust_name", "string"),
        ("col1", "string", "gender", "string"),
        ("col2", "string", "day_of_birth", "timestamp"),
        ("col3", "double", "age", "decimal"),
        ("col4", "string", "email_addr", "string"),
    ],
    transformation_ctx="ApplyMapping_node2",
)

# Custom Transform
Customtransform_node = Encrypt_PII(glueContext, DynamicFrameCollection({"ApplyMapping_node2": ApplyMapping_node2}, glueContext))

# Script generated for node Redshift Cluster
RedshiftCluster_node3 = glueContext.write_dynamic_frame.from_catalog(
    frame=Customtransform_node,
    database="<--AMAZON-REDSHIFT-DATABASE-NAME-->",
    table_name="<--AMAZON-REDSHIFT-TABLE-NAME-->",
    redshift_tmp_dir="<--AMAZON-S3-STAGING-LOCATION-->",
    additional_options={
        "aws_iam_role": "<--ARN-OF-IAM-ROLE-TO-BE-USED-->"
    },
    transformation_ctx="RedshiftCluster_node3",
)

job.commit()
