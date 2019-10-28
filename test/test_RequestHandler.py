import json
import os
import random
import string
import unittest

import boto3
import uuid
from boto3.dynamodb.conditions import Key
from moto import mock_dynamodb2
import arrow as arrow


@mock_dynamodb2
class TestHandlerCase(unittest.TestCase):

    def setUp(self):
        """Mocked AWS Credentials for moto."""
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'

    def tearDown(self):
        pass

    def setup_mock_database(self, table_name):
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        table_connection = dynamodb.create_table(TableName=table_name,
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
                'resource_identifier': 'ebf20333-35a5-4a06-9c58-68ea688a9a8b',
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

    def remove_mock_database(self, dynamodb, table_name):
        dynamodb.Table(table_name).delete()

    def test_retrieve_resource(self):
        from src.classes.RequestHandler import RequestHandler
        table_name = 'testing'
        dynamodb = self.setup_mock_database(table_name)
        request_handler = RequestHandler(dynamodb, table_name)

        retrieve_response = request_handler.retrieve_resource('ebf20333-35a5-4a06-9c58-68ea688a9a8b')

        self.assertEqual(retrieve_response['ResponseMetadata']['HTTPStatusCode'], 200, 'HTTP Status code not 200')
        self.assertEqual(retrieve_response['Items'][0]['resource_identifier'], 'ebf20333-35a5-4a06-9c58-68ea688a9a8b',
                         'Value not retrieved as expected')
        self.remove_mock_database(dynamodb, table_name)

    def test_handler_retrieve_resource(self):
        from src.classes.RequestHandler import RequestHandler
        table_name = 'testing'
        dynamodb = self.setup_mock_database(table_name)
        request_handler = RequestHandler(dynamodb, table_name)

        event = {
            "body": "{\"operation\": \"RETRIEVE\",\"resource\": {\"resource_identifier\": \"ebf20333-35a5-4a06-9c58-68ea688a9a8b\"}}"
        }

        handler_retrieve_response = request_handler.handler(event, None)

        handler_retrieve_response_json = json.loads(handler_retrieve_response['body'])

        self.assertEqual(handler_retrieve_response['statusCode'], 200, 'HTTP Status code not 200')
        self.assertEqual(handler_retrieve_response_json['Items'][0]['resource_identifier'],
                         'ebf20333-35a5-4a06-9c58-68ea688a9a8b', 'Value not retrieved as expected')
        self.remove_mock_database(dynamodb, table_name)


if __name__ == '__main__':
    unittest.main()
