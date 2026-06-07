import boto3

TABLE_NAME = "ai_news"

dynamodb_client = boto3.client("dynamodb")

dynamodb_client.create_table(
    TableName=TABLE_NAME,
    AttributeDefinitions=[
        {"AttributeName": "link", "AttributeType": "S"},
        {"AttributeName": "published_datetime", "AttributeType": "N"},
        {"AttributeName": "category", "AttributeType": "S"}
    ],
    KeySchema=[
        {"AttributeName": "link", "KeyType": "HASH"}
    ],
    GlobalSecondaryIndexes=[
        {'IndexName': 'published_datetime',
         "KeySchema": [
                {"AttributeName": "category", "KeyType": "HASH"},         # 全件を集約するパーティション
                {"AttributeName": "published_datetime", "KeyType": "RANGE"} # 日付でソート
         ],
         'Projection': {'ProjectionType': 'ALL'}
        }
    ],
    BillingMode='PAY_PER_REQUEST'
)

waiter = dynamodb_client.get_waiter('table_exists')
waiter.wait(TableName=TABLE_NAME)

dynamodb_client.update_time_to_live(
   TableName=TABLE_NAME,
   TimeToLiveSpecification={"Enabled": True, "AttributeName": "ttl",},
)

