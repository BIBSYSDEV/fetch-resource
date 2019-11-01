import http
import json
import os
import unittest

import boto3
from moto import mock_dynamodb2

from common.constants import Constants


def unittest_lambda_handler(event, context):
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(TestHandlerCase))


def remove_mock_database(dynamodb):
    dynamodb.Table(os.environ['TABLE_NAME']).delete()


EXISTING_RESOURCE_IDENTIFIER = 'ebf20333-35a5-4a06-9c58-68ea688a9a8b'


@mock_dynamodb2
class TestHandlerCase(unittest.TestCase):

    def setUp(self):
        """Mocked AWS Credentials for moto."""
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'
        os.environ[Constants.ENV_VAR_TABLE_NAME] = 'testing'
        os.environ[Constants.ENV_VAR_REGION] = 'eu-west-1'

    def tearDown(self):
        pass

    def setup_mock_database(self):
        dynamodb = boto3.resource('dynamodb', region_name=os.environ[Constants.ENV_VAR_REGION])
        table_connection = dynamodb.create_table(TableName=os.environ[Constants.ENV_VAR_TABLE_NAME],
                                                 KeySchema=[
                                                     {'AttributeName': 'resource_identifier',
                                                      'KeyType': 'HASH'},
                                                     {'AttributeName': 'modifiedDate',
                                                      'KeyType': 'RANGE'}],
                                                 AttributeDefinitions=[
                                                     {'AttributeName': 'resource_identifier',
                                                      'AttributeType': 'S'},
                                                     {'AttributeName': 'modifiedDate',
                                                      'AttributeType': 'S'}],
                                                 ProvisionedThroughput={'ReadCapacityUnits': 1,
                                                                        'WriteCapacityUnits': 1})
        table_connection.put_item(
            Item={
                'resource_identifier': EXISTING_RESOURCE_IDENTIFIER,
                'modifiedDate': '2019-10-24T12:57:02.655994Z',
                'createdDate': '2019-10-24T12:57:02.655994Z',
                'metadata': {
                    'titles': {
                        'no': 'En tittel'
                    }
                }
            }
        )
        return dynamodb

    def test_app(self):
        from src import app
        self.assertRaises(ValueError, app.handler, None, None)
        event = {
            "body": "{\"operation\": \"UNKNOWN_OPERATION\"} "
        }
        handler_response = app.handler(event, None)
        self.assertEqual(handler_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')

    def test_retrieve_resource(self):
        from src.classes.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database()
        request_handler = RequestHandler(dynamodb)

        retrieve_response = request_handler.retrieve_resource(EXISTING_RESOURCE_IDENTIFIER)

        self.assertEqual(retrieve_response['ResponseMetadata']['HTTPStatusCode'], http.HTTPStatus.OK,
                         'HTTP Status code not 200')
        self.assertEqual(
            retrieve_response[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS][0][Constants.DDB_FIELD_RESOURCE_IDENTIFIER],
            EXISTING_RESOURCE_IDENTIFIER,
            'Value not retrieved as expected')
        remove_mock_database(dynamodb)

    def test_handler_retrieve_resource(self):
        from src.classes.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database()
        request_handler = RequestHandler(dynamodb)

        event = {
            "body": "{\"operation\": \"RETRIEVE\",\"resource\": {\"resource_identifier\": \"ebf20333-35a5-4a06-9c58-68ea688a9a8b\"}}"
        }

        handler_retrieve_response = request_handler.handler(event, None)

        handler_retrieve_response_json = json.loads(handler_retrieve_response[Constants.RESPONSE_BODY])

        self.assertEqual(handler_retrieve_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.OK,
                         'HTTP Status code not 200')
        self.assertEqual(handler_retrieve_response_json[Constants.DDB_RESPONSE_ATTRIBUTE_NAME_ITEMS][0][
                             Constants.DDB_FIELD_RESOURCE_IDENTIFIER],
                         EXISTING_RESOURCE_IDENTIFIER, 'Value not retrieved as expected')
        remove_mock_database(dynamodb)

    def test_handler_retrieve_resource_not_found(self):
        from src.classes.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database()
        request_handler = RequestHandler(dynamodb)

        event = {
            "body": "{\"operation\": \"RETRIEVE\",\"resource\": {\"resource_identifier\": \"fbf20333-35a5-4a06-9c58-68ea688a9a8b\"}}"
        }

        handler_retrieve_response = request_handler.handler(event, None)

        handler_retrieve_response_json = json.loads(handler_retrieve_response[Constants.RESPONSE_BODY])

        self.assertEqual(handler_retrieve_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.NOT_FOUND,
                         'HTTP Status code not 404')
        remove_mock_database(dynamodb)

    def test_handler_retrieve_resource_missing_resource(self):
        from src.classes.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database()
        request_handler = RequestHandler(dynamodb)

        event = {
            "body": "{\"operation\": \"RETRIEVE\"}"
        }

        handler_retrieve_response = request_handler.handler(event, None)

        self.assertEqual(handler_retrieve_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)

    def test_handler_retrieve_resource_missing_resource_identifier(self):
        from src.classes.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database()
        request_handler = RequestHandler(dynamodb)

        event = {
            "body": "{\"operation\": \"RETRIEVE\",\"resource\": {}}"
        }

        handler_retrieve_response = request_handler.handler(event, None)

        self.assertEqual(handler_retrieve_response[Constants.RESPONSE_STATUS_CODE], http.HTTPStatus.BAD_REQUEST,
                         'HTTP Status code not 400')
        remove_mock_database(dynamodb)


if __name__ == '__main__':
    unittest.main()
