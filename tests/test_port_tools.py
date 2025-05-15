#!/usr/bin/env python3
"""
Test module for port scanning tools functionality.

This module contains tests for the port scanning tools module functions including scan_port,
scan_ports, scan_common_ports, and find_service_ports. Tests use mocks to avoid actual
network calls and verify the correct behavior of the functions under various conditions.
"""

import socket
import concurrent.futures
import pytest
from unittest.mock import patch, MagicMock, call
from rich.console import Console
from nettools.port_tools import scan_port, scan_ports, scan_common_ports, find_service_ports

# Mock console for testing
@pytest.fixture
def mock_console():
    """Create a mock console object for testing."""
    with patch('nettools.port_tools.port_scanner.console') as mock_console:
        yield mock_console


class TestScanPort:
    """Test cases for the scan_port function."""

    @patch('socket.socket')
    def test_scan_open_port(self, mock_socket, mock_console):
        """Test scanning a port that is open."""
        # Arrange
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0  # 0 means the port is open
        mock_socket.return_value = mock_sock
        
        # Mock the service name lookup
        with patch('socket.getservbyport', return_value='http'):
            # Act
            result = scan_port('localhost', 80)
        
        # Assert
        assert result == (80, True, 'http')
        mock_sock.connect_ex.assert_called_once_with(('localhost', 80))
        mock_sock.settimeout.assert_called_once()
        mock_sock.close.assert_called_once()

    @patch('socket.socket')
    def test_scan_closed_port(self, mock_socket, mock_console):
        """Test scanning a port that is closed."""
        # Arrange
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 1  # Non-zero means the port is closed
        mock_socket.return_value = mock_sock
        
        # Act
        result = scan_port('localhost', 12345)
        
        # Assert
        assert result == (12345, False, '')
        mock_sock.connect_ex.assert_called_once_with(('localhost', 12345))

    @patch('socket.socket')
    def test_scan_with_invalid_port(self, mock_socket, mock_console):
        """Test scanning with an invalid port number."""
        # Arrange - using a port number outside valid range
        port = 70000  # Valid range is 0-65535
        
        # Act
        result = scan_port('localhost', port)
        
        # Assert
        assert result == (port, False, '')
        mock_console.print.assert_called_with(f"[bold red]Error:[/bold red] Invalid port number: {port}. Port must be between 0 and 65535.")
        mock_socket.assert_not_called()  # Socket should not be created for invalid port

    @patch('socket.socket')
    def test_scan_with_unresolvable_hostname(self, mock_socket, mock_console):
        """Test scanning with a hostname that cannot be resolved."""
        # Arrange
        mock_sock = MagicMock()
        mock_sock.connect_ex.side_effect = socket.gaierror()
        mock_socket.return_value = mock_sock
        
        # Act
        result = scan_port('nonexistent.example', 80)
        
        # Assert
        assert result == (80, False, '')
        mock_console.print.assert_called_with("[bold red]Error:[/bold red] Hostname nonexistent.example could not be resolved")

    @patch('socket.socket')
    def test_scan_with_connection_error(self, mock_socket, mock_console):
        """Test scanning with a connection error."""
        # Arrange
        mock_sock = MagicMock()
        mock_sock.connect_ex.side_effect = socket.error("Connection error")
        mock_socket.return_value = mock_sock
        
        # Act
        result = scan_port('localhost', 80)
        
        # Assert
        assert result == (80, False, '')
        mock_console.print.assert_called_with("[bold red]Error:[/bold red] Could not connect to localhost:80 - Connection error")

    @patch('socket.socket')
    def test_open_port_with_unknown_service(self, mock_socket, mock_console):
        """Test scanning an open port with an unknown service."""
        # Arrange
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0  # Port is open
        mock_socket.return_value = mock_sock
        
        # Mock the service name lookup to raise an exception
        with patch('socket.getservbyport', side_effect=socket.error()):
            # Act
            result = scan_port('localhost', 9999)  # Using a non-standard port
        
        # Assert
        assert result == (9999, True, 'unknown')
        mock_sock.connect_ex.assert_called_once_with(('localhost', 9999))


class TestScanPorts:
    """Test cases for the scan_ports function."""

    @patch('nettools.port_tools.port_scanner._scan_worker')
    @patch('concurrent.futures.ThreadPoolExecutor')
    @patch('time.time')
    def test_scan_ports_list(self, mock_time, mock_executor, mock_scan_worker, mock_console):
        """Test scanning a list of ports."""
        # Arrange
        mock_time.side_effect = [0, 1]  # Start and end time
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Set up mock executor to return scan results
        mock_executor_instance.map.return_value = [
            (80, True, 'http'),
            (443, True, 'https'),
            (22, False, '')
        ]
        
        # Act
        result = scan_ports('example.com', [80, 443, 22], verbose=False)
        
        # Assert
        assert result == [(80, True, 'http'), (443, True, 'https')]  # Only open ports should be returned
        mock_executor_instance.map.assert_called_once()
        assert mock_executor.call_args[1]['max_workers'] == 100

    @patch('nettools.port_tools.port_scanner._scan_worker')
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_scan_ports_range(self, mock_executor, mock_scan_worker, mock_console):
        """Test scanning a range of ports."""
        # Arrange
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Set up mock executor to return scan results
        mock_executor_instance.map.return_value = [
            (80, True, 'http'),
            (81, False, ''),
            (82, False, '')
        ]
        
        # Act
        result = scan_ports('example.com', (80, 82), verbose=False)
        
        # Assert
        assert result == [(80, True, 'http')]  # Only open ports should be returned
        mock_executor_instance.map.assert_called_once()

    @patch('builtins.input')
    @patch('nettools.port_tools.port_scanner._scan_worker')
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_scan_ports_with_user_input_range(self, mock_executor, mock_scan_worker, mock_input, mock_console):
        """Test scanning ports with user input for a range."""
        # Arrange
        mock_input.side_effect = ['example.com', '80-82']
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Set up mock executor to return scan results
        mock_executor_instance.map.return_value = [
            (80, True, 'http'),
            (81, False, ''),
            (82, False, '')
        ]
        
        # Act
        result = scan_ports(verbose=False)
        
        # Assert
        assert result == [(80, True, 'http')]
        mock_input.assert_called()
        assert mock_input.call_count == 2
        mock_executor_instance.map.assert_called_once()

    @patch('builtins.input')
    @patch('nettools.port_tools.port_scanner._scan_worker')
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_scan_ports_with_user_input_comma_separated(self, mock_executor, mock_scan_worker, mock_input, mock_console):
        """Test scanning ports with user input for comma separated ports."""
        # Arrange
        mock_input.side_effect = ['example.com', '22,80,443']
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Set up mock executor to return scan results
        mock_executor_instance.map.return_value = [
            (22, False, ''),
            (80, True, 'http'),
            (443, True, 'https')
        ]
        
        # Act
        result = scan_ports(verbose=False)
        
        # Assert
        assert result == [(80, True, 'http'), (443, True, 'https')]
        mock_input.assert_called()
        assert mock_input.call_count == 2
        mock_executor_instance.map.assert_called_once()

    @patch('nettools.port_tools.port_scanner._scan_worker')
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_scan_ports_with_invalid_port(self, mock_executor, mock_scan_worker, mock_console):
        """Test scanning with an invalid port range."""
        # Arrange
        port_range = [70000]  # Invalid port number
        
        # Act
        result = scan_ports('example.com', port_range, verbose=False)
        
        # Assert
        assert result == []
        mock_console.print.assert_called_with("[bold red]Error:[/bold red] Invalid port number: 70000. Port must be between 0 and 65535.")
        mock_executor.assert_not_called()

    @patch('nettools.port_tools.port_scanner._scan_worker')
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_scan_ports_with_invalid_range_format(self, mock_executor, mock_scan_worker, mock_console):
        """Test scanning with an invalid port range format."""
        # Arrange
        port_range = "invalid"  # Not a tuple or list
        
        # Act
        result = scan_ports('example.com', port_range, verbose=False)
        
        # Assert
        assert result == []
        mock_console.print.assert_called_with("[bold red]Error:[/bold red] Invalid port range format")
        mock_executor.assert_not_called()


class TestScanCommonPorts:
    """Test cases for the scan_common_ports function."""

    @patch('nettools.port_tools.port_scanner.scan_ports')
    def test_scan_common_ports(self, mock_scan_ports, mock_console):
        """Test scanning common ports."""
        # Arrange
        mock_scan_ports.return_value = [
            (80, True, 'http'),
            (443, True, 'https')
        ]
        
        # Act
        result = scan_common_ports('example.com')
        
        # Assert
        assert result == [(80, True, 'http'), (443, True, 'https')]
        mock_scan_ports.assert_called_once()
        # Verify the correct common ports list was passed (contains at least 20 common ports)
        assert len(mock_scan_ports.call_args[0][1]) >= 20
        assert 80 in mock_scan_ports.call_args[0][1]  # HTTP port should be included
        assert 443 in mock_scan_ports.call_args[0][1]  # HTTPS port should be included

    @patch('builtins.input')
    @patch('nettools.port_tools.port_scanner.scan_ports')
    def test_scan_common_ports_with_user_input(self, mock_scan_ports, mock_input, mock_console):
        """Test scanning common ports with user input."""
        # Arrange
        mock_input.return_value = 'example.com'
        mock_scan_ports.return_value = [(22, True, 'ssh')]
        
        # Act
        result = scan_common_ports()
        
        # Assert
        assert result == [(22, True, 'ssh')]
        mock_input.assert_called_once()
        mock_scan_ports.assert_called_once()


class TestFindServicePorts:
    """Test cases for the find_service_ports function."""

    def test_find_common_service_port(self, mock_console):
        """Test finding ports for a common service."""
        # Act
        result = find_service_ports('http', verbose=False)
        
        # Assert
        assert 80 in result  # HTTP port should be in results

    @patch('socket.getservbyname')
    def test_find_custom_service_port(self, mock_getservbyname, mock_console):
        """Test finding ports for a custom service."""
        # Arrange
        mock_getservbyname.return_value = 8080
        
        # Act
        result = find_service_ports('custom-http', verbose=False)
        
        # Assert
        assert 8080 in result
        mock_getservbyname.assert_called_once_with('custom-http')

    @patch('socket.getservbyname')
    def test_find_nonexistent_service(self, mock_getservbyname, mock_console):
        """Test finding ports for a nonexistent service."""
        # Arrange
        mock_getservbyname.side_effect = socket.error()
        
        # Act
        result = find_service_ports('nonexistent-service', verbose=False)
        
        # Assert
        assert result == []
        mock_getservbyname.assert_called_once_with('nonexistent-service')

    @patch('socket.getservbyname')
    def test_find_service_port_handles_error(self, mock_getservbyname, mock_console):
        """Test that find_service_ports handles unexpected errors."""
        # Arrange
        mock_getservbyname.side_effect = Exception("Unexpected error")
        
        # Act
        result = find_service_ports('http', verbose=False)
        
        # Assert
        assert 80 in result  # Should still find HTTP from common services dictionary
        mock_getservbyname.assert_called_once_with('http')
        mock_console.print.assert_called_with("[bold red]Error:[/bold red] Unexpected error")

    def test_find_service_partial_match(self, mock_console):
        """Test finding service with partial name match."""
        # Act - using "mail" which should match "smtp", "imap", etc.
        result = find_service_ports('mail', verbose=False)
        
        # Assert - should find multiple mail-related ports
        assert len(result) > 0
        # Common mail ports like 25 (SMTP) should be included
        assert 25 in result or 143 in result  # SMTP or IMAP