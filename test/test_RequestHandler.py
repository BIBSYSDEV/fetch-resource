import json
import os
import unittest

import boto3
from moto import mock_dynamodb2


def unittest_lambda_handler(event, context):
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(TestHandlerCase))


@mock_dynamodb2
class TestHandlerCase(unittest.TestCase):

    def setUp(self):
        """Mocked AWS Credentials for moto."""
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'
        os.environ['TABLE_NAME'] = 'testing'
        os.environ['REGION'] = 'eu-west-1'

    def tearDown(self):
        pass

    def setup_mock_database(self):
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])
        table_connection = dynamodb.create_table(TableName=os.environ['TABLE_NAME'],
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

    def remove_mock_database(self, dynamodb):
        dynamodb.Table(os.environ['TABLE_NAME']).delete()

    def test_app(self):
        from src import app
        self.assertRaises(ValueError, app.handler, None, None)
        event = {
            "body": "{\"operation\": \"UNKNOWN_OPERATION\"} "
        }
        handler_response = app.handler(event, None)
        self.assertEqual(handler_response['statusCode'], 400, 'HTTP Status code not 400')

    def test_retrieve_resource(self):
        from src.classes.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database()
        request_handler = RequestHandler(dynamodb)

        retrieve_response = request_handler.retrieve_resource('ebf20333-35a5-4a06-9c58-68ea688a9a8b')

        self.assertEqual(retrieve_response['ResponseMetadata']['HTTPStatusCode'], 200, 'HTTP Status code not 200')
        self.assertEqual(retrieve_response['Items'][0]['resource_identifier'], 'ebf20333-35a5-4a06-9c58-68ea688a9a8b',
                         'Value not retrieved as expected')
        self.remove_mock_database(dynamodb)

    def test_handler_retrieve_resource(self):
        from src.classes.RequestHandler import RequestHandler
        dynamodb = self.setup_mock_database()
        request_handler = RequestHandler(dynamodb)

        event = {
            "body": "{\"operation\": \"RETRIEVE\",\"resource\": {\"resource_identifier\": \"ebf20333-35a5-4a06-9c58-68ea688a9a8b\"}}"
        }

        handler_retrieve_response = request_handler.handler(event, None)

        handler_retrieve_response_json = json.loads(handler_retrieve_response['body'])

        self.assertEqual(handler_retrieve_response['statusCode'], 200, 'HTTP Status code not 200')
        self.assertEqual(handler_retrieve_response_json['Items'][0]['resource_identifier'],
                         'ebf20333-35a5-4a06-9c58-68ea688a9a8b', 'Value not retrieved as expected')
        self.remove_mock_database(dynamodb)


if __name__ == '__main__':
    unittest.main()
