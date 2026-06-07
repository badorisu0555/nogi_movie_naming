# python
import json
from unittest.mock import patch
from fastapi.responses import JSONResponse
from app.batch.main import main


def test_main_success():
    with patch("app.tweet_cat_API.tweet_api.get_tweet") as mock_get_tweet, \
         patch("app.tweet_cat_API.preprocessing.load_and_preprocess_data") as mock_preprocess, \
         patch("app.tweet_cat_API.tweet_categorize.categorize_tweets_with_LLM") as mock_categorize:

        mock_get_tweet.return_value = ("/tmp/save.json", [{"id": 1, "text": "tweet"}])
        mock_preprocess.return_value = {"df": "json"}
        expected = {"result": "ok"}
        mock_categorize.return_value = expected

        result = main("query-string", tweet_cnt=5)

        assert result == expected
        mock_get_tweet.assert_called_once_with("query-string", 5)
        mock_preprocess.assert_called_once_with("/tmp/save.json")
        mock_categorize.assert_called_once_with({"df": "json"})


def test_main_get_tweet_exception():
    with patch("app.tweet_cat_API.tweet_api.get_tweet", side_effect=Exception("fetch failed")):
        res = main("q", tweet_cnt=1)
        assert isinstance(res, JSONResponse)
        assert res.status_code == 500
        body = json.loads(res.body.decode())
        assert "error" in body and "fetch failed" in body["error"]


def test_main_categorize_exception():
    with patch("app.tweet_cat_API.tweet_api.get_tweet") as mock_get_tweet, \
         patch("app.tweet_cat_API.preprocessing.load_and_preprocess_data") as mock_preprocess, \
         patch("app.tweet_cat_API.tweet_categorize.categorize_tweets_with_LLM", side_effect=RuntimeError("llm fail")):

        mock_get_tweet.return_value = ("/tmp/save.json", [])
        mock_preprocess.return_value = {"df": "json"}

        res = main("q2", tweet_cnt=2)
        assert isinstance(res, JSONResponse)
        assert res.status_code == 500
        body = json.loads(res.body.decode())
        assert "error" in body and "llm fail" in body["error"]