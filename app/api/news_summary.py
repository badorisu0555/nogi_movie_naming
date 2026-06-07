import pandas as pd
import boto3
import json
from botocore.exceptions import ClientError
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

def load_api_key():
    # override=True にすることで、.env のセットアップが既存の環境変数を上書きします
    env_path = os.path.join(os.path.dirname(__file__), "../../.env")
    load_dotenv(dotenv_path=env_path, override=True)
    os.environ["AWS_BEARER_TOKEN_BEDROCK"] = os.getenv("Bedrock_API_Key")

def create_response(prompt_text,news_data):
    client = boto3.client("bedrock-runtime")

    prompt = PromptTemplate(
        input_variables=["news_data"],
        template = prompt_text)
    prompt = prompt.format(news_data=news_data)

    body = json.dumps({
        "messages":[
            {"role":"user","content":prompt}
        ],
        "max_tokens":4096,
        "temperature":0.5,
        "anthropic_version":"bedrock-2023-05-31"
    })

    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    response = client.invoke_model(
        modelId=model_id,
        body=body
    )

    return response

def summarize_news_with_LLM(news_data):
    load_api_key()

    prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
    f = open(prompt_path,"r",encoding="utf-8")
    prompt_text = f.read()
    response = create_response(prompt_text,news_data)

    response_body = json.loads(response.get("body").read())
    answer = response_body["content"][0]["text"]
    return answer

# 動作確認
if __name__ == "__main__":
     summarize_news_with_LLM()