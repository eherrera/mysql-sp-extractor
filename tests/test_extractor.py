import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
from datetime import datetime
from dotenv import load_dotenv
from mysql_sp_extractor.extractor import StoredProcedureExtractor

# Load environment variables
load_dotenv()

class TestStoredProcedureExtractor(unittest.TestCase):
    def setUp(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'test_user'),
            'password': os.getenv('DB_PASS', 'test_pass'),
            'database': os.getenv('DB_NAME', 'test_db')
        }
        self.extractor = StoredProcedureExtractor(**self.config)

    @patch('mysql.connector.connect')
    def test_connect_success(self, mock_connect):
        mock_connect.return_value = MagicMock()
        self.assertTrue(self.extractor.connect())
        mock_connect.assert_called_once_with(**self.config)


    @patch('mysql.connector.connect')
    def test_disconnect(self, mock_connect):
        conn_mock = MagicMock()
        conn_mock.is_connected.return_value = True
        mock_connect.return_value = conn_mock
        self.extractor.connect()
        self.extractor.disconnect()
        conn_mock.close.assert_called_once()

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_create_output_directory_new(self, mock_makedirs, mock_exists):
        mock_exists.return_value = False
        self.extractor.create_output_directory()
        mock_makedirs.assert_called_once_with(self.extractor.output_dir)

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_create_output_directory_existing(self, mock_makedirs, mock_exists):
        mock_exists.return_value = True
        self.extractor.create_output_directory()
        mock_makedirs.assert_not_called()

    @patch('mysql.connector.connect')
    def test_get_routines(self, mock_connect):
        cursor_mock = MagicMock()
        cursor_mock.fetchall.return_value = [('proc1', 'PROCEDURE'), ('proc2', 'PROCEDURE')]
        conn_mock = MagicMock()
        conn_mock.cursor.return_value = cursor_mock
        mock_connect.return_value = conn_mock
        
        self.extractor.connect()
        routines = self.extractor.get_routines()
        
        self.assertEqual(len(routines), 2)
        self.assertEqual(routines[0], ('proc1', 'PROCEDURE'))

    @patch('mysql.connector.connect')
    def test_get_routine_definition(self, mock_connect):
        cursor_mock = MagicMock()
        cursor_mock.fetchone.return_value = ('proc1', 'utf8', 'CREATE PROCEDURE proc1...')
        conn_mock = MagicMock()
        conn_mock.cursor.return_value = cursor_mock
        mock_connect.return_value = conn_mock
        
        self.extractor.connect()
        definition = self.extractor.get_routine_definition('proc1')
        
        self.assertEqual(definition, 'CREATE PROCEDURE proc1...')

    @patch('builtins.open', new_callable=mock_open)
    def test_save_routine(self, mock_file):
        result = self.extractor.save_routine('test_proc', 'CREATE PROCEDURE test_proc...')
        self.assertTrue(result)
        mock_file.assert_called_once()

    @patch('mysql.connector.connect')
    def test_extract_all(self, mock_connect):
        conn_mock = MagicMock()
        cursor_mock = MagicMock()
        
        # Mock get_routines responses
        cursor_mock.fetchall.side_effect = [
            [('proc1', 'PROCEDURE')],  # For procedures
            [('func1', 'FUNCTION')]    # For functions
        ]
        
        # Mock get_routine_definition responses
        cursor_mock.fetchone.side_effect = [
            ('proc1', 'utf8', 'CREATE PROCEDURE proc1...'),
            ('func1', 'utf8', 'CREATE FUNCTION func1...')
        ]
        
        conn_mock.cursor.return_value = cursor_mock
        conn_mock.is_connected.return_value = True
        mock_connect.return_value = conn_mock
        
        self.extractor.conn = conn_mock
        
        with patch('builtins.open', new_callable=mock_open()):
            results = self.extractor.extract_all()
            
        self.assertEqual(results['procedures'], 1)
        self.assertEqual(results['functions'], 1)

if __name__ == '__main__':
    unittest.main()