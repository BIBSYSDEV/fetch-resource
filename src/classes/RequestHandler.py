import json
import os

import boto3
from boto3.dynamodb.conditions import Key
from boto3_type_annotations.dynamodb import Table

from common.constants import Constants


class RequestHandler:

    def __init__(self, dynamodb=None):
        if dynamodb is None:
            self.dynamodb = boto3.resource('dynamodb', region_name=os.environ[Constants.ENV_VAR_REGION])
        else:
            self.dynamodb = dynamodb

        self.table_name = os.environ.get(Constants.ENV_VAR_TABLE_NAME)
        self.table: Table = self.dynamodb.Table(self.table_name)

    def retrieve_resource(self, uuid):
        ddb_response = self.table.query(
            KeyConditionExpression=Key(Constants.DDB_FIELD_RESOURCE_IDENTIFIER).eq(uuid),
            ScanIndexForward=True
        )
        return ddb_response

    def handler(self, event, context):
        operation = json.loads(event[Constants.EVENT_BODY]).get(Constants.JSON_ATTRIBUTE_NAME_OPERATION)
        resource = json.loads(event[Constants.EVENT_BODY]).get(Constants.JSON_ATTRIBUTE_NAME_RESOURCE)

        if operation == Constants.OPERATION_RETRIEVE:
            uuid = resource['resource_identifier']
            ddb_response = self.retrieve_resource(uuid)
            return {
                Constants.RESPONSE_STATUS_CODE: 200,
                Constants.RESPONSE_BODY: json.dumps(ddb_response)
            }
        else:
            return {
                Constants.RESPONSE_STATUS_CODE: 400,
                Constants.RESPONSE_BODY: 'Insufficient parameters'
            }
