import http
import json
import os

import boto3
from boto3.dynamodb.conditions import Key
from boto3_type_annotations.dynamodb import Table
from common.constants import Constants

from common.helpers import response


class RequestHandler:

    def __init__(self, dynamodb=None):
        if dynamodb is None:
            self.dynamodb = boto3.resource(Constants.DDB, region_name=os.environ[Constants.ENV_VAR_REGION])
        else:
            self.dynamodb = dynamodb

        self.table_name = os.environ.get(Constants.ENV_VAR_TABLE_NAME)
        self.table: Table = self.dynamodb.Table(self.table_name)

    def __retrieve_resource(self, uuid):
        _ddb_response = self.table.query(
            KeyConditionExpression=Key(Constants.DDB_FIELD_RESOURCE_IDENTIFIER).eq(uuid),
            ScanIndexForward=True
        )
        return _ddb_response

    def handler(self, event, context):
        if event is None or Constants.EVENT_PATH_PARAMETERS not in event:
            return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)

        if Constants.EVENT_PATH_PARAMETER_IDENTIFIER not in event[Constants.EVENT_PATH_PARAMETERS]:
            return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)

        _identifier = event[Constants.EVENT_PATH_PARAMETERS][Constants.EVENT_PATH_PARAMETER_IDENTIFIER]
        _http_method = event[Constants.EVENT_HTTP_METHOD]

        if _http_method == Constants.HTTP_METHOD_GET and len(_identifier) > 0:
            _ddb_response = self.__retrieve_resource(_identifier)
            if len(_ddb_response[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS]) == 0:
                return response(http.HTTPStatus.NOT_FOUND, json.dumps(_ddb_response))
            return response(http.HTTPStatus.OK, json.dumps(_ddb_response))
        return response(http.HTTPStatus.BAD_REQUEST, Constants.ERROR_INSUFFICIENT_PARAMETERS)