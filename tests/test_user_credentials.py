"""
Unit tests for UserCredentials class
"""

import unittest
from unittest.mock import patch
import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import UserCredentials


class TestUserCredentials(unittest.TestCase):
    """Test cases for UserCredentials class"""
    
    def test_email_property_with_complete_email(self):
        """Test email property when account already contains @ symbol"""
        credentials = UserCredentials(
            account="test@example.com",
            password="password123"
        )
        
        with patch('main.logger') as mock_logger:
            result = credentials.email
            
            self.assertEqual(result, "test@example.com")
            mock_logger.info.assert_called_once_with("Using complete email address: test@example.com")
    
    def test_email_property_with_username_only(self):
        """Test email property when account is just username"""
        credentials = UserCredentials(
            account="12345678",
            password="password123"
        )
        
        with patch('main.logger') as mock_logger:
            result = credentials.email
            
            expected = "12345678@nkust.edu.tw"
            self.assertEqual(result, expected)
            mock_logger.info.assert_called_once_with(f"Auto-appended default domain: {expected}")
    
    def test_email_property_with_different_domain(self):
        """Test email property with different school domain"""
        credentials = UserCredentials(
            account="student@ntu.edu.tw",
            password="password123"
        )
        
        with patch('main.logger') as mock_logger:
            result = credentials.email
            
            self.assertEqual(result, "student@ntu.edu.tw")
            mock_logger.info.assert_called_once_with("Using complete email address: student@ntu.edu.tw")
    
    def test_email_property_with_empty_account(self):
        """Test email property with empty account"""
        credentials = UserCredentials(
            account="",
            password="password123"
        )
        
        with patch('main.logger') as mock_logger:
            result = credentials.email
            
            expected = "@nkust.edu.tw"
            self.assertEqual(result, expected)
            mock_logger.info.assert_called_once_with(f"Auto-appended default domain: {expected}")


if __name__ == '__main__':
    unittest.main()
