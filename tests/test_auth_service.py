"""
Unit tests for AuthService class
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import AuthService, UserCredentials, AuthToken


class TestAuthService(unittest.TestCase):
    """Test cases for AuthService class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.auth_service = AuthService()
    
    def test_init(self):
        """Test AuthService initialization"""
        self.assertIsNotNone(self.auth_service.session)
        self.assertEqual(self.auth_service.login_url, "https://irs.zuvio.com.tw/irs/submitLogin")
    
    def test_login_success(self):
        """Test successful login"""
        credentials = UserCredentials(account="test@example.com", password="password123")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'''
        <script>
            var user_id = "12345";
            var accessToken = "abc123token";
        </script>
        '''
        
        with patch.object(self.auth_service.session, 'post', return_value=mock_response):
            with patch.object(self.auth_service, '_extract_tokens') as mock_extract:
                mock_token = AuthToken(user_id="12345", access_token="abc123token")
                mock_extract.return_value = mock_token
                
                result = self.auth_service.login(credentials)
                
                self.assertIsNotNone(result)
                self.assertEqual(result.user_id, "12345")
                self.assertEqual(result.access_token, "abc123token")
    
    def test_login_request_exception(self):
        """Test login with request exception"""
        credentials = UserCredentials(account="test@example.com", password="password123")
        
        with patch.object(self.auth_service.session, 'post', side_effect=Exception("Network error")):
            with patch('main.logger') as mock_logger:
                result = self.auth_service.login(credentials)
                
                self.assertIsNone(result)
                mock_logger.error.assert_called()
    
    def test_extract_tokens_success(self):
        """Test successful token extraction"""
        html_content = b'''
        <script>
            var user_id = "12345";
            var accessToken = "abc123token";
        </script>
        '''
        
        result = self.auth_service._extract_tokens(html_content)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.user_id, "12345")
        self.assertEqual(result.access_token, "abc123token")
    
    def test_extract_tokens_no_scripts(self):
        """Test token extraction when no scripts found"""
        html_content = b'<html><body>No scripts here</body></html>'
        
        with patch('main.logger') as mock_logger:
            result = self.auth_service._extract_tokens(html_content)
            
            self.assertIsNone(result)
            mock_logger.error.assert_called_with("無法找到認證Token")
    
    def test_extract_tokens_exception(self):
        """Test token extraction with exception"""
        html_content = b'invalid html content'
        
        with patch('main.logger') as mock_logger:
            result = self.auth_service._extract_tokens(html_content)
            
            self.assertIsNone(result)
            mock_logger.error.assert_called()
    
    def test_extract_tokens_with_quoted_user_id(self):
        """Test token extraction with quoted user_id"""
        html_content = b'''
        <script>
            var user_id = "12345";
            var accessToken = "abc123token";
        </script>
        '''
        
        result = self.auth_service._extract_tokens(html_content)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.user_id, "12345")  # Should strip quotes
        self.assertEqual(result.access_token, "abc123token")
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        credentials = UserCredentials(account="invalid@example.com", password="wrongpass")
        
        # Mock failed response
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Unauthorized")
        
        with patch.object(self.auth_service.session, 'post', return_value=mock_response):
            with patch('main.logger') as mock_logger:
                result = self.auth_service.login(credentials)
                
                self.assertIsNone(result)
                mock_logger.error.assert_called()


if __name__ == '__main__':
    unittest.main()
