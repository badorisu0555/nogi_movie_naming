import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    # SSMから注入された環境変数を取得
    api_key = os.getenv("Bedrock_API_Key", "Not Found")
    
    # セキュリティのため、最初の4文字だけ表示して残りは伏せる
    masked_key = api_key[:4] + "*" * (len(api_key) - 4) if api_key != "Not Found" else "Not Found"
    
    return {
        "status": "running",
        "message": "Hello from ECS Fargate!",
        "detected_api_key": masked_key
    }