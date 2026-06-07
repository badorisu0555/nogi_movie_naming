import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
from fastapi.testclient import TestClient
from app.api.main import app
from app.api.get_dynamod_data import get_dynamo_data
from app.api.news_summary import summarize_news_with_LLM


client = TestClient(app)


class TestApiHealthCheck:
    """Tests for API health check endpoint"""
    
    def test_root_endpoint_success(self):
        """Test root endpoint returns healthy status"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "healthy"


class TestGetDynamoData:
    """Tests for get_dynamo_data function"""
    
    @patch("app.api.get_dynamod_data.boto3.client")
    @patch("app.api.get_dynamod_data.boto3.resource")
    def test_get_dynamo_data_success(self, mock_resource, mock_client):
        """Test successful data retrieval from DynamoDB"""
        # Mock dynamodb resource
        mock_dynamodb = MagicMock()
        mock_resource.return_value = mock_dynamodb
        
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        
        mock_response = {
            'Items': [
                {
                    'id': '001',
                    'title': 'Test News',
                    'link': 'https://example.com',
                    'published_datetime': 1234567890,
                    'category': 'AI_news',
                    'summary': 'Test summary'
                }
            ]
        }
        mock_table.query.return_value = mock_response
        
        result = get_dynamo_data(days=7, table_name='test-project')
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['title'] == 'Test News'
        mock_table.query.assert_called_once()
    
    @patch("app.api.get_dynamod_data.boto3.client")
    @patch("app.api.get_dynamod_data.boto3.resource")
    def test_get_dynamo_data_empty_result(self, mock_resource, mock_client):
        """Test when no items are found in DynamoDB"""
        mock_dynamodb = MagicMock()
        mock_resource.return_value = mock_dynamodb
        
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        
        mock_response = {'Items': []}
        mock_table.query.return_value = mock_response
        
        result = get_dynamo_data(days=7, table_name='test-project')
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @patch("app.api.get_dynamod_data.boto3.client")
    @patch("app.api.get_dynamod_data.boto3.resource")
    def test_get_dynamo_data_multiple_items(self, mock_resource, mock_client):
        """Test retrieval of multiple items from DynamoDB"""
        mock_dynamodb = MagicMock()
        mock_resource.return_value = mock_dynamodb
        
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        
        mock_response = {
            'Items': [
                {'id': '001', 'title': 'News 1', 'published_datetime': 1234567890},
                {'id': '002', 'title': 'News 2', 'published_datetime': 1234567891},
                {'id': '003', 'title': 'News 3', 'published_datetime': 1234567892}
            ]
        }
        mock_table.query.return_value = mock_response
        
        result = get_dynamo_data(days=7, table_name='test-project')
        
        assert len(result) == 3
        assert result[0]['title'] == 'News 1'
        assert result[2]['title'] == 'News 3'
    
    @patch("app.api.get_dynamod_data.boto3.client")
    @patch("app.api.get_dynamod_data.boto3.resource")
    def test_get_dynamo_data_custom_days(self, mock_resource, mock_client):
        """Test with custom days parameter"""
        mock_dynamodb = MagicMock()
        mock_resource.return_value = mock_dynamodb
        
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        
        mock_response = {'Items': []}
        mock_table.query.return_value = mock_response
        
        result = get_dynamo_data(days=30, table_name='test-project')
        
        assert isinstance(result, list)
        mock_table.query.assert_called_once()
    
    @patch("app.api.get_dynamod_data.boto3.resource")
    def test_get_dynamo_data_exception(self, mock_resource):
        """Test exception handling in get_dynamo_data"""
        mock_resource.side_effect = Exception("DynamoDB connection failed")
        
        with pytest.raises(Exception, match="DynamoDB connection failed"):
            get_dynamo_data(days=7, table_name='test-project')


class TestSummarizeNewsWithLLM:
    """Tests for summarize_news_with_LLM function"""
    
    @patch("app.api.news_summary.load_api_key")
    @patch("builtins.open", new_callable=mock_open, read_data="Test prompt template")
    @patch("app.api.news_summary.boto3.client")
    def test_summarize_news_success(self, mock_boto3_client, mock_file, mock_load_api):
        """Test successful news summarization with LLM"""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        mock_response = {
            'body': MagicMock(read=lambda: json.dumps({
                'content': [{'text': 'Test summary output'}]
            }).encode())
        }
        mock_client.invoke_model.return_value = mock_response
        
        test_news_data = [
            {
                'title': 'Test Article',
                'link': 'https://example.com',
                'summary': 'Test summary'
            }
        ]
        
        result = summarize_news_with_LLM(test_news_data)
        
        assert result == 'Test summary output'
        assert mock_client.invoke_model.called
    
    @patch("app.api.news_summary.load_api_key")
    @patch("builtins.open", new_callable=mock_open, read_data="Test prompt with {news_data}")
    @patch("app.api.news_summary.boto3.client")
    def test_summarize_news_with_multiple_articles(self, mock_boto3_client, mock_file, mock_load_api):
        """Test summarization with multiple articles"""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        mock_response = {
            'body': MagicMock(read=lambda: json.dumps({
                'content': [{'text': 'Multiple article summary'}]
            }).encode())
        }
        mock_client.invoke_model.return_value = mock_response
        
        test_news_data = [
            {'title': 'Article 1', 'link': 'https://example.com/1'},
            {'title': 'Article 2', 'link': 'https://example.com/2'},
            {'title': 'Article 3', 'link': 'https://example.com/3'}
        ]
        
        result = summarize_news_with_LLM(test_news_data)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @patch("app.api.news_summary.load_api_key")
    @patch("builtins.open", new_callable=mock_open, read_data="Test prompt")
    @patch("app.api.news_summary.boto3.client")
    def test_summarize_news_empty_data(self, mock_boto3_client, mock_file, mock_load_api):
        """Test summarization with empty news data"""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        mock_response = {
            'body': MagicMock(read=lambda: json.dumps({
                'content': [{'text': 'No news to summarize'}]
            }).encode())
        }
        mock_client.invoke_model.return_value = mock_response
        
        result = summarize_news_with_LLM([])
        
        assert isinstance(result, str)
    
    @patch("app.api.news_summary.load_api_key")
    @patch("builtins.open", new_callable=mock_open, read_data="Test prompt")
    @patch("app.api.news_summary.boto3.client")
    def test_summarize_news_llm_exception(self, mock_boto3_client, mock_file, mock_load_api):
        """Test exception handling in LLM call"""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        mock_client.invoke_model.side_effect = Exception("LLM service unavailable")
        
        test_news_data = [{'title': 'Test', 'link': 'https://example.com'}]
        
        with pytest.raises(Exception, match="LLM service unavailable"):
            summarize_news_with_LLM(test_news_data)


class TestPredictEndpoint:
    """Tests for /predict endpoint"""
    
    @patch("app.api.main.news_summary.summarize_news_with_LLM")
    @patch("app.api.main.get_dynamod_data.get_dynamo_data")
    def test_predict_endpoint_success(self, mock_get_data, mock_summarize):
        """Test successful prediction endpoint"""
        mock_get_data.return_value = [
            {
                'title': 'Test News',
                'link': 'https://example.com',
                'published_datetime': 1234567890
            }
        ]
        mock_summarize.return_value = '{"result": "success"}'
        
        response = client.get("/predict")
        
        assert response.status_code == 200
        mock_get_data.assert_called_once()
        mock_summarize.assert_called_once()
    
    @patch("app.api.main.news_summary.summarize_news_with_LLM")
    @patch("app.api.main.get_dynamod_data.get_dynamo_data")
    def test_predict_endpoint_with_custom_days(self, mock_get_data, mock_summarize):
        """Test prediction endpoint with custom days parameter"""
        mock_get_data.return_value = []
        mock_summarize.return_value = '{"result": "no data"}'
        
        response = client.get("/predict?days=30")
        
        assert response.status_code == 200
        mock_get_data.assert_called_once()
    
    @patch("app.api.main.get_dynamod_data.get_dynamo_data")
    def test_predict_endpoint_get_data_exception(self, mock_get_data):
        """Test error handling when data retrieval fails"""
        mock_get_data.side_effect = Exception("Database error")
        
        response = client.get("/predict")
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "Database error" in data["error"]
    
    @patch("app.api.main.news_summary.summarize_news_with_LLM")
    @patch("app.api.main.get_dynamod_data.get_dynamo_data")
    def test_predict_endpoint_summarize_exception(self, mock_get_data, mock_summarize):
        """Test error handling when summarization fails"""
        mock_get_data.return_value = [{'title': 'Test', 'link': 'https://example.com'}]
        mock_summarize.side_effect = Exception("LLM error")
        
        response = client.get("/predict")
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "LLM error" in data["error"]
    
    @patch("app.api.main.news_summary.summarize_news_with_LLM")
    @patch("app.api.main.get_dynamod_data.get_dynamo_data")
    def test_predict_endpoint_with_table_name_param(self, mock_get_data, mock_summarize):
        """Test prediction endpoint with custom table name"""
        mock_get_data.return_value = []
        mock_summarize.return_value = '{"result": "success"}'
        
        response = client.get("/predict?table_name=custom-table")
        
        assert response.status_code == 200
        call_args = mock_get_data.call_args
        assert call_args[1]['table_name'] == 'custom-table'


class TestNewsDataIntegration:
    """Integration tests for news data flow through API"""
    
    @patch("app.api.main.news_summary.summarize_news_with_LLM")
    @patch("app.api.main.get_dynamod_data.get_dynamo_data")
    def test_full_api_pipeline(self, mock_get_data, mock_summarize):
        """Test complete API pipeline from data retrieval to summarization"""
        # Mock data from DynamoDB
        mock_get_data.return_value = [
            {
                'id': '20260205101',
                'title': 'OpenAI Announcement',
                'link': 'https://openai.com/news',
                'published_datetime': 1770217200,
                'category': 'AI_news',
                'summary': 'New AI model released'
            },
            {
                'id': '20260205102',
                'title': 'Google AI Update',
                'link': 'https://google.com/ai',
                'published_datetime': 1770217201,
                'category': 'AI_news',
                'summary': 'Gemini update announced'
            }
        ]
        
        # Mock summarization output
        mock_summarize.return_value = json.dumps([
            {
                'link': 'https://openai.com/news',
                'category': 'Tech/Library',
                'priority': 'High',
                'reason': 'Important AI model release'
            },
            {
                'link': 'https://google.com/ai',
                'category': 'Tech/Library',
                'priority': 'Medium',
                'reason': 'Regular product update'
            }
        ])
        
        response = client.get("/predict?days=7")
        
        assert response.status_code == 200
        assert mock_get_data.call_count == 1
        assert mock_summarize.call_count == 1
        
        # Verify the data was passed correctly
        summarize_call_args = mock_summarize.call_args[0][0]
        assert len(summarize_call_args) == 2
        assert summarize_call_args[0]['title'] == 'OpenAI Announcement'
