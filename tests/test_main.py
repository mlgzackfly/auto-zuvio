"""
Integration tests for main module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main, ZuvioAutoChecker


class TestMain(unittest.TestCase):
    """Integration test cases for main module"""
    
    def test_main_function(self):
        """Test main function execution"""
        with patch.object(ZuvioAutoChecker, 'run') as mock_run:
            main()
            mock_run.assert_called_once()
    
    def test_main_module_imports(self):
        """Test that main module can be imported without errors"""
        try:
            import main
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import main module: {e}")
    
    def test_main_module_has_required_classes(self):
        """Test that main module has all required classes"""
        import main
        
        required_classes = [
            'UserCredentials',
            'Location', 
            'AuthToken',
            'ConfigManager',
            'AuthService',
            'CourseService',
            'ZuvioAutoChecker'
        ]
        
        for class_name in required_classes:
            self.assertTrue(hasattr(main, class_name), f"Missing class: {class_name}")
    
    def test_main_module_has_required_functions(self):
        """Test that main module has all required functions"""
        import main
        
        required_functions = ['main']
        
        for func_name in required_functions:
            self.assertTrue(hasattr(main, func_name), f"Missing function: {func_name}")
    
    @patch('builtins.print')
    def test_main_execution_with_keyboard_interrupt(self, mock_print):
        """Test main function handles KeyboardInterrupt gracefully"""
        with patch.object(ZuvioAutoChecker, 'run', side_effect=KeyboardInterrupt):
            main()
            # Should not raise exception
    
    @patch('builtins.print')
    def test_main_execution_with_general_exception(self, mock_print):
        """Test main function handles general exceptions gracefully"""
        with patch.object(ZuvioAutoChecker, 'run', side_effect=Exception("Test error")):
            try:
                main()
                # Should not raise exception
                self.assertTrue(True)
            except Exception:
                self.fail("main() should handle exceptions gracefully")


if __name__ == '__main__':
    unittest.main()
