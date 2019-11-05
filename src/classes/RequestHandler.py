import http
import json
import os

import boto3
from boto3.dynamodb.conditions import Key
from boto3_type_annotations.dynamodb import Table

from common.constants import Constants


def response(status_code, body):
    return {
        Constants.RESPONSE_STATUS_CODE: status_code,
        Constants.RESPONSE_BODY: body
    }


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
        if event is None or Constants.EVENT_BODY not in event:
            return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)

        body = json.loads(event[Constants.EVENT_BODY])
        http_method = event[Constants.EVENT_HTTP_METHOD]
        resource = body.get(Constants.JSON_ATTRIBUTE_NAME_RESOURCE)

        if http_method == Constants.HTTP_METHOD_GET and resource is not None and Constants.DDB_FIELD_RESOURCE_IDENTIFIER in resource:
            uuid = resource['resource_identifier']
            ddb_response = self.retrieve_resource(uuid)
            if len(ddb_response[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS]) == 0:
                return response(http.HTTPStatus.NOT_FOUND, json.dumps(ddb_response))
            return response(http.HTTPStatus.OK, json.dumps(ddb_response))
        return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)
