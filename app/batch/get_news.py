import feedparser
import pandas as pd
import json
from datetime import datetime
from bs4 import BeautifulSoup
import os

def parse_text(entry,today,id_1,id_2,id_3,category,news_df):
    # published_parsedをintオブジェクトに変換
    struct_time = entry.published_parsed
    dt = datetime(*struct_time[:6])
    published_datetime = dt.timestamp()
    published_datetime = int(published_datetime)

    # TTLの設定
    ttl = 14*24*60*60  # 14日間のTTLを秒単位で計算
    ttl = published_datetime + ttl

    print(f"ID: {today}{id_1}{id_2}{id_3}")
    print(f"カテゴリー: {category}")
    print(f"タイトル: {entry.title}")
    print(f"リンク: {entry.link}")
    print(f"公開日時 (datetime): {dt}")
    print(f"概要: {entry.summary}")
    print(f"TTL時間: {ttl}")

    addRow = [f"{today}{id_1}{id_2}{id_3}", category,  entry.title, entry.link, published_datetime, entry.summary, ttl]
    addRow = pd.DataFrame([addRow], columns=["id", "category", "title", "link", "published_datetime", "summary", "ttl"])
    news_df = pd.concat([news_df, addRow], ignore_index=True)
    print("-" * 30)

    if id_3 == 9:
        id_2 += 1

    if id_3 == 9:
        id_3 = 0
    else:
        id_3 += 1

    return news_df, id_2, id_3

def get_news_data(RSS_list):
    id_1 = 1
    today = datetime.now().strftime("%Y%m%d")
    category = "AI_news"
    news_df = pd.DataFrame()

    for url in RSS_list:
        feed = feedparser.parse(url)
        id_2 = 0
        id_3 = 1
        for entry in feed.entries[0:1]:
            news_df, id_2, id_3 = parse_text(entry,today,id_1,id_2,id_3,category,news_df)
        id_1 += 1

    return news_df

# HTMLタグを除去する関数
def clean_html(html, strip=False):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(strip=strip)
    return text

def get_news():
# 1. このスクリプト(get_news.py)が存在するディレクトリの絶対パスを取得
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 2. RSS.jsonへの絶対パスを生成
    json_path = os.path.join(base_dir, 'RSS.json')

    # 生成したパスでファイルを開く
    with open(json_path, encoding='utf-8') as f:
        RSS_list = json.load(f)

    news_df = get_news_data(RSS_list)
    if 'summary' in news_df.columns:
        news_df["summary"] = news_df["summary"].apply(lambda x: clean_html(x, strip=True))
    else:
        print("Warning: 'summary' column is missing.")
    return news_df

if __name__ == "__main__":
    get_news()