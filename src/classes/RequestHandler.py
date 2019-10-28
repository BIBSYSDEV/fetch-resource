import decimal
import json

import boto3
from boto3.dynamodb.conditions import Key
from boto3_type_annotations.dynamodb import Table
import os


class RequestHandler:

    def __init__(self, dynamodb=None, table_name=None):
        if dynamodb is None:
            self.dynamodb = boto3.resource('dynamodb')
        else:
            self.dynamodb = dynamodb

        if table_name is None:
            self.table_name = os.environ.get("TABLE_NAME")
        else:
            self.table_name = table_name

        self.table: Table = self.dynamodb.Table(self.table_name)

    def get_table_connection(self):
        return self.table

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
            raise ValueError("Unknown operation")


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
