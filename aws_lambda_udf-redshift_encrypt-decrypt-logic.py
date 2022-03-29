import boto3
import json
import base64
import logging
from miscreant.aes.siv import SIV

logger = logging.getLogger()
logger.setLevel(logging.INFO)

secret_name = '<--ARN-OF-YOUR-SECRETS-MANAGER-SECRET-NAME-->'

sm_client = boto3.client('secretsmanager')
get_secret_value_response = sm_client.get_secret_value(SecretId = secret_name)  # Skip error-handling logic for dev/test purpose only
data_encryption_key = get_secret_value_response['SecretBinary']

siv = SIV(data_encryption_key)  # Without nonce, the encryption becomes deterministic

def lambda_handler(event, context):
  ret = dict()
  res = []
  action = event['external_function'].split('_')[1]
  if (action == 'encrypt' or action == 'decrypt'):
      for argument in event['arguments']:
          try:
              columnValue = argument[0]
              if (columnValue == None):
                  response = None
              else:
                  if action == 'encrypt':
                      ciphertext = siv.seal(columnValue.encode())
                      response = base64.b64encode(ciphertext).decode('utf-8')
                  else:
                      plaintext = siv.open(base64.b64decode(columnValue))
                      response = plaintext.decode('utf-8')
              res.append(response)
          except Exception as e:
              print("[DEBUG] Exception: " + str(e))
              res.append(None)
      ret['success'] = True
      ret['results'] = res
  else:
      ret['success'] = False
      ret['error_msg'] = 'Invalid action'
  return json.dumps(ret)
