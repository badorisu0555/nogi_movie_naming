import pandas as pd
import boto3
from botocore.exceptions import ClientError
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import numpy as np


# 一括書き込み。batch_writerを使用すると、DynamoDBの制限に基づいて自動的にバッチを分割してくれる。
def dynamo_batch_write(news_df, table_name, region_name='ap-northeast-1'):
    news_data = news_df.to_dict(orient='records')
    #JSONファイルの読み込み
    # dynamodbの設定
    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    table = dynamodb.Table(table_name)

    with table.batch_writer() as batch:
        for item in news_data:
            item_not_has_nan = {key: item[key] for key in item if item[key] is not np.nan}
            batch.put_item(Item=item_not_has_nan)
    print(f"Successfully wrote {len(news_data)} items to {table_name} table.")
    return "Successfully wrote to DynamoDB"

# 動作確認
if __name__ == "__main__":
    # テスト用のサンプルデータを作成
    sample_data = {
        'title': ['Sample News 1', 'Sample News 2'],
        'content': ['Content 1', 'Content 2'],
    }
    news_df = pd.DataFrame(sample_data)
    table_name = 'ai_news'
    dynamo_batch_write(news_df, table_name, region_name='ap-northeast-1')

# 動作確認
if __name__ == "__main__":
    dynamo_batch_write(news_df, table_name, region_name='ap-northeast-1')
