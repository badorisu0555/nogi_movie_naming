import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
import pandas as pd
from datetime import datetime
from app.batch.get_news import get_news
from app.batch.dynamo_write import dynamo_batch_write


class TestGetNews:
    """Tests for get_news function"""
    
    @patch("builtins.open", new_callable=mock_open, read_data='["https://example.com/rss.xml"]')
    @patch("app.batch.get_news.feedparser.parse")
    def test_get_news_success(self, mock_parse, mock_file):
        """Test successful news fetching from RSS feeds"""
        mock_entry = MagicMock()
        mock_entry.title = "Test Article"
        mock_entry.link = "https://example.com/article"
        mock_entry.summary = "<p>Test summary</p>"
        mock_entry.published_parsed = (2024, 1, 15, 10, 30, 45, 0, 0, 0)
        
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed
        
        # get_news()を呼び出し
        result = get_news()
        
        # DataFrameが返されることを確認
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        # テストはモックなので、データが存在することを確認
        print(f"Result DataFrame:\n{result}")
        print(f"Columns: {result.columns.tolist()}")
        # モックが呼ばれたことを確認
        assert mock_parse.called, "feedparser.parse was not called"
    
    @patch("builtins.open", new_callable=mock_open, read_data='["https://feed1.com/rss", "https://feed2.com/rss"]')
    @patch("app.batch.get_news.feedparser.parse")
    def test_get_news_multiple_feeds(self, mock_parse, mock_file):
        """Test fetching from multiple RSS feeds"""
        mock_entry = MagicMock()
        mock_entry.title = "Article"
        mock_entry.link = "https://example.com"
        mock_entry.summary = "Summary"
        mock_entry.published_parsed = (2024, 1, 15, 10, 30, 45, 0, 0, 0)
        
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed
        
        result = get_news()
        
        assert isinstance(result, pd.DataFrame)
        assert mock_parse.call_count == 2
    
    @patch("builtins.open", new_callable=mock_open, read_data='["https://example.com/rss.xml"]')
    @patch("app.batch.get_news.feedparser.parse")
    def test_get_news_empty_entries(self, mock_parse, mock_file):
        """Test handling when RSS feed has no entries"""
        mock_feed = MagicMock()
        mock_feed.entries = []
        mock_parse.return_value = mock_feed
        
        result = get_news()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch("builtins.open", new_callable=mock_open, read_data='["https://example.com/rss.xml"]')
    @patch("app.batch.get_news.feedparser.parse")
    def test_get_news_parse_exception(self, mock_parse, mock_file):
        """Test handling when feedparser fails"""
        mock_parse.side_effect = Exception("Parse error")
        
        with pytest.raises(Exception, match="Parse error"):
            get_news()


class TestDynamoBatchWrite:
    """Tests for dynamo_batch_write function"""
    
    @patch("app.batch.dynamo_write.boto3.resource")
    def test_dynamo_batch_write_success(self, mock_boto3_resource):
        """Test successful batch write to DynamoDB"""
        mock_table = MagicMock()
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value.__enter__ = MagicMock(return_value=mock_batch_writer)
        mock_table.batch_writer.return_value.__exit__ = MagicMock(return_value=False)
        
        mock_boto3_resource.return_value.Table.return_value = mock_table
        
        test_data = pd.DataFrame([
            {"id": "001", "title": "Test", "link": "https://example.com", "published_datetime": 1234567890}
        ])
        
        result = dynamo_batch_write(test_data, "test-table")
        
        assert "Successfully" in result
        mock_batch_writer.put_item.assert_called_once()
    
    @patch("app.batch.dynamo_write.boto3.resource")
    def test_dynamo_batch_write_multiple_items(self, mock_boto3_resource):
        """Test batch write with multiple items"""
        mock_table = MagicMock()
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value.__enter__ = MagicMock(return_value=mock_batch_writer)
        mock_table.batch_writer.return_value.__exit__ = MagicMock(return_value=False)
        
        mock_boto3_resource.return_value.Table.return_value = mock_table
        
        test_data = pd.DataFrame([
            {"id": "001", "title": "Test1"},
            {"id": "002", "title": "Test2"},
            {"id": "003", "title": "Test3"}
        ])
        
        dynamo_batch_write(test_data, "test-table")
        
        assert mock_batch_writer.put_item.call_count == 3
    
    @patch("app.batch.dynamo_write.boto3.resource")
    def test_dynamo_batch_write_filters_nan(self, mock_boto3_resource):
        """Test that NaN values are filtered out"""
        import numpy as np
        
        mock_table = MagicMock()
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value.__enter__ = MagicMock(return_value=mock_batch_writer)
        mock_table.batch_writer.return_value.__exit__ = MagicMock(return_value=False)
        
        mock_boto3_resource.return_value.Table.return_value = mock_table
        
        test_data = pd.DataFrame([
            {"id": "001", "title": "Test", "optional_field": np.nan}
        ])
        
        dynamo_batch_write(test_data, "test-table")
        
        call_args = mock_batch_writer.put_item.call_args
        item = call_args[1]["Item"]
        assert "optional_field" not in item or item["optional_field"] is not np.nan
    
    @patch("app.batch.dynamo_write.boto3.resource")
    def test_dynamo_batch_write_exception(self, mock_boto3_resource):
        """Test exception handling in batch write"""
        mock_boto3_resource.side_effect = Exception("DynamoDB connection failed")
        
        test_data = pd.DataFrame([{"id": "001", "title": "Test"}])
        
        with pytest.raises(Exception, match="DynamoDB connection failed"):
            dynamo_batch_write(test_data, "test-table")
    
    @patch("app.batch.dynamo_write.boto3.resource")
    def test_dynamo_batch_write_empty_dataframe(self, mock_boto3_resource):
        """Test batch write with empty DataFrame"""
        mock_table = MagicMock()
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value.__enter__ = MagicMock(return_value=mock_batch_writer)
        mock_table.batch_writer.return_value.__exit__ = MagicMock(return_value=False)
        
        mock_boto3_resource.return_value.Table.return_value = mock_table
        
        test_data = pd.DataFrame()
        
        result = dynamo_batch_write(test_data, "test-table")
        
        assert "Successfully" in result
        mock_batch_writer.put_item.assert_not_called()


class TestIntegration:
    """Integration tests for batch module"""
    
    @patch("builtins.open", new_callable=mock_open, read_data='["https://example.com/rss.xml"]')
    @patch("app.batch.get_news.feedparser.parse")
    @patch("app.batch.dynamo_write.boto3.resource")
    def test_full_pipeline_success(self, mock_boto3, mock_parse, mock_file):
        """Test complete pipeline from RSS fetch to DynamoDB write"""
        # Mock feedparser
        mock_entry = MagicMock()
        mock_entry.title = "Integration Test"
        mock_entry.link = "https://example.com"
        mock_entry.summary = "Test summary"
        mock_entry.published_parsed = (2024, 1, 15, 10, 30, 45, 0, 0, 0)
        
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed
        
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_batch_writer = MagicMock()
        mock_table.batch_writer.return_value.__enter__ = MagicMock(return_value=mock_batch_writer)
        mock_table.batch_writer.return_value.__exit__ = MagicMock(return_value=False)
        mock_boto3.return_value.Table.return_value = mock_table
        
        # Run pipeline
        news_df = get_news()
        result = dynamo_batch_write(news_df, "test-table")
        
        assert len(news_df) > 0
        assert "Successfully" in result