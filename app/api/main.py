from app.api import get_dynamod_data
from app.api import news_summary
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "AI news summary API healthy", "status": "healthy"}

@app.get("/predict")
def main(days=7,table_name='ai_news'):
    try:
        print("=======================ニュースデータの取得を開始します。=======================")
        news_data = get_dynamod_data.get_dynamo_data(days=days, table_name=table_name)
        print(f"=======================ニュースデータの取得が完了しました。=======================")
        print(news_data)
        print("=======================ニュースの要約を開始します。=======================")
        summary = news_summary.summarize_news_with_LLM(news_data)
        print("=======================ニュースの要約が完了しました。=======================")
        print(summary)
        return summary
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
