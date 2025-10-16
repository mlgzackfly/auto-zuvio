"""
Unit tests for ZuvioAutoChecker class
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import ZuvioAutoChecker, UserCredentials, AuthToken, Location


class TestZuvioAutoChecker(unittest.TestCase):
    """Test cases for ZuvioAutoChecker class"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch('main.ConfigManager'), \
             patch('main.AuthService'):
            self.checker = ZuvioAutoChecker()
    
    def test_init(self):
        """Test ZuvioAutoChecker initialization"""
        self.assertIsNotNone(self.checker.config_manager)
        self.assertIsNotNone(self.checker.auth_service)
        self.assertIsNone(self.checker.course_service)
        self.assertTrue(self.checker.running)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_setup_user_credentials_new_user(self, mock_print, mock_input):
        """Test setting up credentials for new user"""
        mock_input.side_effect = ['test@example.com', 'password123']
        
        with patch.object(self.checker.config_manager, 'get_user_credentials', return_value=None), \
             patch.object(self.checker.config_manager, 'save_user_credentials') as mock_save:
            
            credentials = self.checker.setup_user_credentials()
            
            self.assertEqual(credentials.account, 'test@example.com')
            self.assertEqual(credentials.password, 'password123')
            mock_save.assert_called_once()
    
    def test_setup_user_credentials_existing_user(self):
        """Test setting up credentials for existing user"""
        existing_credentials = UserCredentials(account='existing@example.com', password='existingpass')
        
        with patch.object(self.checker.config_manager, 'get_user_credentials', return_value=existing_credentials):
            credentials = self.checker.setup_user_credentials()
            
            self.assertEqual(credentials.account, 'existing@example.com')
            self.assertEqual(credentials.password, 'existingpass')
    
    def test_test_login_and_setup_success_first_attempt(self):
        """Test successful login on first attempt"""
        credentials = UserCredentials(account='test@example.com', password='password123')
        auth_token = AuthToken(user_id='12345', access_token='abc123')
        
        with patch.object(self.checker.auth_service, 'login', return_value=auth_token), \
             patch('builtins.print') as mock_print:
            
            result = self.checker.test_login_and_setup(credentials)
            
            self.assertEqual(result, auth_token)
            mock_print.assert_called_with("登入測試成功！")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_test_login_and_setup_retry_success(self, mock_print, mock_input):
        """Test successful login after retry"""
        credentials = UserCredentials(account='test@example.com', password='password123')
        auth_token = AuthToken(user_id='12345', access_token='abc123')
        
        mock_input.return_value = 'y'
        
        with patch.object(self.checker.auth_service, 'login') as mock_login, \
             patch.object(self.checker.config_manager, 'save_user_credentials'):
            
            # First attempt fails, second succeeds
            mock_login.side_effect = [None, auth_token]
            
            result = self.checker.test_login_and_setup(credentials)
            
            self.assertEqual(result, auth_token)
            self.assertEqual(mock_login.call_count, 2)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_test_login_and_setup_max_attempts_exceeded(self, mock_print, mock_input):
        """Test login failure after max attempts"""
        credentials = UserCredentials(account='test@example.com', password='password123')
        
        mock_input.return_value = 'y'
        
        with patch.object(self.checker.auth_service, 'login', return_value=None), \
             patch.object(self.checker.config_manager, 'save_user_credentials'):
            
            result = self.checker.test_login_and_setup(credentials)
            
            self.assertIsNone(result)
            mock_print.assert_called_with("已達到最大嘗試次數，登入失敗")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_setup_location_new_location(self, mock_print, mock_input):
        """Test setting up new location"""
        mock_input.side_effect = ['120.123', '22.456']
        
        with patch.object(self.checker.config_manager, 'get_location', return_value=None), \
             patch.object(self.checker.config_manager, 'save_location') as mock_save:
            
            location = self.checker.setup_location()
            
            self.assertEqual(location.longitude, '120.123')
            self.assertEqual(location.latitude, '22.456')
            mock_save.assert_called_once()
    
    def test_setup_location_existing_location(self):
        """Test setup with existing location"""
        existing_location = Location(latitude='22.123', longitude='120.456')
        
        with patch.object(self.checker.config_manager, 'get_location', return_value=existing_location):
            location = self.checker.setup_location()
            
            self.assertEqual(location.latitude, '22.123')
            self.assertEqual(location.longitude, '120.456')
    
    @patch('builtins.print')
    def test_display_courses(self, mock_print):
        """Test displaying course list"""
        courses = [
            {'course_name': 'Course 1', 'teacher_name': 'Teacher 1'},
            {'course_name': 'Course 2', 'teacher_name': 'Teacher 2'}
        ]
        
        with patch('main.datetime') as mock_datetime:
            mock_datetime.today.return_value.strftime.return_value = '2024/01/01'
            
            self.checker.display_courses(courses)
            
            # Should print date and course information
            self.assertTrue(mock_print.called)
    
    def test_run_checkin_loop_with_available_course(self):
        """Test check-in loop with available course"""
        auth_token = AuthToken(user_id='12345', access_token='abc123')
        location = Location(latitude='22.123', longitude='120.456')
        courses = [{'course_name': 'Test Course', 'course_id': 'course1'}]
        
        with patch.object(self.checker.course_service, 'check_rollcall_availability', return_value='rollcall123'), \
             patch.object(self.checker.course_service, 'perform_checkin', return_value=(True, "簽到成功！")), \
             patch('builtins.print'), \
             patch('time.sleep'), \
             patch('main.datetime') as mock_datetime:
            
            mock_datetime.now.return_value.strftime.return_value = '12:00:00'
            
            # Set running to False after first iteration to prevent infinite loop
            def stop_loop():
                self.checker.running = False
            
            with patch('time.sleep', side_effect=stop_loop):
                self.checker.run_checkin_loop(auth_token, courses, location)
    
    def test_run_checkin_loop_no_available_courses(self):
        """Test check-in loop with no available courses"""
        auth_token = AuthToken(user_id='12345', access_token='abc123')
        location = Location(latitude='22.123', longitude='120.456')
        courses = [{'course_name': 'Test Course', 'course_id': 'course1'}]
        
        with patch.object(self.checker.course_service, 'check_rollcall_availability', return_value=None), \
             patch('builtins.print'), \
             patch('main.datetime') as mock_datetime:
            
            mock_datetime.now.return_value.strftime.return_value = '12:00:00'
            
            # Set running to False after first iteration
            def stop_loop():
                self.checker.running = False
            
            with patch('time.sleep', side_effect=stop_loop):
                self.checker.run_checkin_loop(auth_token, courses, location)


if __name__ == '__main__':
    unittest.main()
