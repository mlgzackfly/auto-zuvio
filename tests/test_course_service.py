"""
Unit tests for CourseService class
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import CourseService, AuthToken, Location


class TestCourseService(unittest.TestCase):
    """Test cases for CourseService class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_session = MagicMock()
        self.course_service = CourseService(self.mock_session)
        self.auth_token = AuthToken(user_id="12345", access_token="abc123token")
        self.location = Location(latitude="22.123", longitude="120.456")
    
    def test_init(self):
        """Test CourseService initialization"""
        self.assertEqual(self.course_service.session, self.mock_session)
        self.assertEqual(len(self.course_service.signed_courses), 0)
    
    def test_get_courses_success(self):
        """Test successful course retrieval"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'status': True,
            'courses': [
                {
                    'course_name': 'Test Course 1',
                    'teacher_name': 'Teacher 1',
                    'course_id': 'course1'
                },
                {
                    'course_name': 'Zuvio Official',
                    'teacher_name': 'Zuvio Staff',
                    'course_id': 'zuvio1'
                },
                {
                    'course_name': 'Test Course 2',
                    'teacher_name': 'Teacher 2',
                    'course_id': 'course2'
                }
            ]
        }
        
        self.mock_session.get.return_value = mock_response
        
        result = self.course_service.get_courses(self.auth_token)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)  # Should filter out Zuvio official
        self.assertEqual(result[0]['course_name'], 'Test Course 1')
        self.assertEqual(result[1]['course_name'], 'Test Course 2')
    
    def test_get_courses_failed_status(self):
        """Test course retrieval with failed status"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': False}
        
        self.mock_session.get.return_value = mock_response
        
        with patch('main.logger') as mock_logger:
            result = self.course_service.get_courses(self.auth_token)
            
            self.assertIsNone(result)
            mock_logger.error.assert_called_with("取得課程資料失敗")
    
    def test_get_courses_request_exception(self):
        """Test course retrieval with request exception"""
        import requests
        self.mock_session.get.side_effect = requests.RequestException("Network error")
        
        with patch('main.logger') as mock_logger:
            result = self.course_service.get_courses(self.auth_token)
            
            self.assertIsNone(result)
            mock_logger.error.assert_called()
    
    def test_get_courses_json_decode_error(self):
        """Test course retrieval with JSON decode error"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        self.mock_session.get.return_value = mock_response
        
        with patch('main.logger') as mock_logger:
            result = self.course_service.get_courses(self.auth_token)
            
            self.assertIsNone(result)
            mock_logger.error.assert_called()
    
    def test_check_rollcall_availability_success(self):
        """Test successful rollcall availability check"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'''
        <script>
            var rollcall_id = 'rollcall123';
        </script>
        '''
        
        self.mock_session.get.return_value = mock_response
        
        result = self.course_service.check_rollcall_availability('course1')
        
        self.assertEqual(result, 'rollcall123')
    
    def test_check_rollcall_availability_no_scripts(self):
        """Test rollcall availability check with no scripts"""
        mock_response = MagicMock()
        mock_response.content = b'<html><body>No scripts</body></html>'
        
        self.mock_session.get.return_value = mock_response
        
        result = self.course_service.check_rollcall_availability('course1')
        
        self.assertIsNone(result)
    
    def test_check_rollcall_availability_exception(self):
        """Test rollcall availability check with exception"""
        self.mock_session.get.side_effect = Exception("Network error")
        
        with patch('main.logger') as mock_logger:
            result = self.course_service.check_rollcall_availability('course1')
            
            self.assertIsNone(result)
            mock_logger.error.assert_called()
    
    def test_perform_checkin_success(self):
        """Test successful check-in"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'status': True}
        
        self.mock_session.post.return_value = mock_response
        
        with patch('main.logger') as mock_logger:
            success, message = self.course_service.perform_checkin(
                self.auth_token, 'rollcall123', self.location
            )
            
            self.assertTrue(success)
            self.assertEqual(message, "簽到成功！")
            mock_logger.info.assert_called_with("簽到成功 (Rollcall ID: rollcall123)")
    
    def test_perform_checkin_failed(self):
        """Test failed check-in"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'status': False,
            'msg': '簽到已結束'
        }
        
        self.mock_session.post.return_value = mock_response
        
        with patch('main.logger') as mock_logger:
            success, message = self.course_service.perform_checkin(
                self.auth_token, 'rollcall123', self.location
            )
            
            self.assertFalse(success)
            self.assertEqual(message, "簽到失敗：簽到已結束")
            mock_logger.warning.assert_called_with("簽到失敗: 簽到已結束")
    
    def test_perform_checkin_request_exception(self):
        """Test check-in with request exception"""
        self.mock_session.post.side_effect = Exception("Network error")
        
        with patch('main.logger') as mock_logger:
            success, message = self.course_service.perform_checkin(
                self.auth_token, 'rollcall123', self.location
            )
            
            self.assertFalse(success)
            self.assertIn("簽到請求失敗", message)
            mock_logger.error.assert_called()
    
    def test_perform_checkin_json_decode_error(self):
        """Test check-in with JSON decode error"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        self.mock_session.post.return_value = mock_response
        
        with patch('main.logger') as mock_logger:
            success, message = self.course_service.perform_checkin(
                self.auth_token, 'rollcall123', self.location
            )
            
            self.assertFalse(success)
            self.assertIn("解析簽到回應失敗", message)
            mock_logger.error.assert_called()


if __name__ == '__main__':
    unittest.main()
