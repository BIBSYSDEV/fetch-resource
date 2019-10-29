import json
import os

import boto3
from boto3.dynamodb.conditions import Key
from boto3_type_annotations.dynamodb import Table


class RequestHandler:

    def __init__(self, dynamodb=None):
        if dynamodb is None:
            self.dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])
        else:
            self.dynamodb = dynamodb

        self.table_name = os.environ.get("TABLE_NAME")
        self.table: Table = self.dynamodb.Table(self.table_name)

    def retrieve_resource(self, uuid):
        ddb_response = self.table.query(
            KeyConditionExpression=Key('resource_identifier').eq(uuid),
            ScanIndexForward=True
        )
        return ddb_response

    def handler(self, event, context):
        operation = json.loads(event['body']).get('operation')
        resource = json.loads(event['body']).get('resource')

        if operation == 'RETRIEVE':
            uuid = resource['resource_identifier']
            ddb_response = self.retrieve_resource(uuid)
            return {
                'statusCode': 200,
                'body': json.dumps(ddb_response),
                'headers': {'Content-Type': 'application/json'}
            }
        else:
            return {
                'statusCode': 400,
                'body': 'insufficient parameters'
            }


