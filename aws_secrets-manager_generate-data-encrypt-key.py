from Crypto.Random import get_random_bytes
import boto3

key = get_random_bytes(32) # 256-bit key size
client = boto3.client('secretsmanager')

response = client.create_secret(
    Name='<--YOUR-SECRETS-MANAGER-SECRET-NAME-->',
    SecretBinary=key
)

print(response)