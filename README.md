# fetch-resource

Performs a search on a given resource_identifier on DynamoDB

### Testing using local sam-dynamodb-local

Follow steps to deploy application at: <https://github.com/ganshan/sam-dynamodb-local>

TLDR:

    docker run -p 8000:8000 amazon/dynamodb-local
    aws dynamodb create-table --cli-input-json file://test/create-local-table.json --endpoint-url http://localhost:8000
    sam build
    sam local start-api --env-vars test/sam-local-envs.json

You should now be able to fetch a resource by its resource_identifier:
    
    curl -v -X GET 'http://127.0.0.1:3000/' -d '{\"resource\": {\"resource_identifier\": \"ebf20333-35a5-4a06-9c58-68ea688a9a8b\"}}'