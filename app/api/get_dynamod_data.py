import pandas as pd
import boto3
import time
from boto3.dynamodb.conditions import Key, Attr


# 一括書き込み。batch_writerを使用すると、DynamoDBの制限に基づいて自動的にバッチを分割してくれる。
def get_dynamo_data(days=7, table_name='ai_news'):
    ut = time.time()
    START_TIME = int(ut - days*24*60*60) # 7日間の範囲指定
    END_TIME = int(ut) #現在の時間

    client = boto3.client('dynamodb', region_name='ap-northeast-1')
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table = dynamodb.Table(table_name)

    response = table.query(
        IndexName = "published_datetime",
        KeyConditionExpression=(
            Key("category").eq("AI_news") &
            Key("published_datetime").between(START_TIME, END_TIME)
        )
    )

    items = response.get('Items', [])
    return items

# 動作確認
if __name__ == "__main__":
    get_dynamo_data(days=7, table_name='ai_news')
