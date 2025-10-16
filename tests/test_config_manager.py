"""
Unit tests for ConfigManager class
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os
import sys

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import ConfigManager, UserCredentials, Location
from secure_input import set_file_permissions


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini')
        self.temp_file.close()
        self.config_manager = ConfigManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_init_with_default_config_file(self):
        """Test ConfigManager initialization with default config file"""
        config_manager = ConfigManager()
        self.assertEqual(config_manager.config_file, "config.ini")
    
    def test_init_with_custom_config_file(self):
        """Test ConfigManager initialization with custom config file"""
        config_manager = ConfigManager("custom.ini")
        self.assertEqual(config_manager.config_file, "custom.ini")
    
    def test_load_config_file_exists(self):
        """Test loading configuration when file exists"""
        # Create a test config file
        test_config = """
[user]
account = test@example.com
password = testpass

[location]
lat = 22.123
lng = 120.456
"""
        with open(self.temp_file.name, 'w') as f:
            f.write(test_config)
        
        self.config_manager.load_config()
        
        self.assertTrue('user' in self.config_manager.config.sections())
        self.assertTrue('location' in self.config_manager.config.sections())
    
    def test_load_config_file_not_exists(self):
        """Test loading configuration when file doesn't exist"""
        # Use a non-existent file
        config_manager = ConfigManager("non_existent.ini")
        config_manager.load_config()
        
        # Should not raise exception, config should be empty
        self.assertEqual(len(config_manager.config.sections()), 0)
    
    def test_save_config(self):
        """Test saving configuration to file"""
        self.config_manager.config.add_section('test')
        self.config_manager.config['test']['key'] = 'value'
        
        with patch('builtins.open', mock_open()) as mock_file:
            self.config_manager.save_config()
            mock_file.assert_called_once_with(self.temp_file.name, 'w', encoding='utf-8')
    
    def test_get_user_credentials_success(self):
        """Test getting user credentials when they exist"""
        self.config_manager.config.add_section('user')
        self.config_manager.config['user']['account'] = 'test@example.com'
        self.config_manager.config['user']['password'] = 'testpass'
        
        credentials = self.config_manager.get_user_credentials()
        
        self.assertIsNotNone(credentials)
        self.assertEqual(credentials.account, 'test@example.com')
        self.assertEqual(credentials.password, 'testpass')
    
    def test_get_user_credentials_not_exists(self):
        """Test getting user credentials when they don't exist"""
        credentials = self.config_manager.get_user_credentials()
        self.assertIsNone(credentials)
    
    def test_save_user_credentials(self):
        """Test saving user credentials"""
        credentials = UserCredentials(account='test@example.com', password='testpass')
        
        with patch.object(self.config_manager, 'save_config') as mock_save:
            self.config_manager.save_user_credentials(credentials)
            
            self.assertTrue('user' in self.config_manager.config.sections())
            self.assertEqual(self.config_manager.config['user']['account'], 'test@example.com')
            self.assertEqual(self.config_manager.config['user']['password'], 'testpass')
            mock_save.assert_called_once()
    
    def test_get_location_success(self):
        """Test getting location when it exists"""
        self.config_manager.config.add_section('location')
        self.config_manager.config['location']['lat'] = '22.123'
        self.config_manager.config['location']['lng'] = '120.456'
        
        location = self.config_manager.get_location()
        
        self.assertIsNotNone(location)
        self.assertEqual(location.latitude, '22.123')
        self.assertEqual(location.longitude, '120.456')
    
    def test_get_location_not_exists(self):
        """Test getting location when it doesn't exist"""
        location = self.config_manager.get_location()
        self.assertIsNone(location)
    
    def test_save_location(self):
        """Test saving location"""
        location = Location(latitude='22.123', longitude='120.456')
        
        with patch.object(self.config_manager, 'save_config') as mock_save:
            self.config_manager.save_location(location)
            
            self.assertTrue('location' in self.config_manager.config.sections())
            self.assertEqual(self.config_manager.config['location']['lat'], '22.123')
            self.assertEqual(self.config_manager.config['location']['lng'], '120.456')
            mock_save.assert_called_once()


if __name__ == '__main__':
    unittest.main()
