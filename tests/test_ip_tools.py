#!/usr/bin/env python3
"""
Test module for IP tools functionality.

This module contains tests for the IP tools module functions including resolve_ip,
analyze_subnet, and ping. Tests use mocks to avoid actual network calls and
verify the correct behavior of the functions under various conditions.
"""

import socket
import ipaddress
import subprocess
import platform
import pytest
from unittest.mock import patch, MagicMock
from rich.console import Console
from nettools.ip_tools import resolve_ip, analyze_subnet, ping

# Mock console for testing
@pytest.fixture
def mock_console():
    """Create a mock console object for testing."""
    with patch('nettools.ip_tools.ip_utils.console') as mock_console:
        yield mock_console


class TestResolveIP:
    """Test cases for the resolve_ip function."""

    @patch('socket.gethostbyname')
    def test_resolve_valid_hostname(self, mock_gethostbyname, mock_console):
        """Test resolving a valid hostname to IP address."""
        # Arrange
        mock_gethostbyname.return_value = '192.0.2.1'
        hostname = 'example.com'
        
        # Act
        result = resolve_ip(hostname)
        
        # Assert
        assert result == '192.0.2.1'
        mock_gethostbyname.assert_called_once_with(hostname)
        mock_console.print.assert_called_with(f"IP address for {hostname}: {result}")

    @patch('socket.gethostbyname')
    def test_resolve_invalid_hostname(self, mock_gethostbyname, mock_console):
        """Test handling of an invalid hostname that cannot be resolved."""
        # Arrange
        mock_gethostbyname.side_effect = socket.gaierror()
        hostname = 'invalid-hostname.invalid'
        
        # Act
        result = resolve_ip(hostname)
        
        # Assert
        assert result is None
        mock_gethostbyname.assert_called_once_with(hostname)
        mock_console.print.assert_called_with(f"[bold red]Error:[/bold red] Could not resolve IP address for {hostname}")

    @patch('builtins.input')
    @patch('socket.gethostbyname')
    def test_resolve_with_user_input(self, mock_gethostbyname, mock_input, mock_console):
        """Test resolving IP with user input for hostname."""
        # Arrange
        mock_input.return_value = 'example.org'
        mock_gethostbyname.return_value = '192.0.2.2'
        
        # Act
        result = resolve_ip()
        
        # Assert
        assert result == '192.0.2.2'
        mock_input.assert_called_once()
        mock_gethostbyname.assert_called_once_with('example.org')


class TestAnalyzeSubnet:
    """Test cases for the analyze_subnet function."""

    @pytest.fixture
    def mock_network(self):
        """Create a mock ipaddress.ip_network for testing."""
        mock = MagicMock()
        mock.network_address = ipaddress.IPv4Address('192.168.1.0')
        mock.broadcast_address = ipaddress.IPv4Address('192.168.1.255')
        mock.num_addresses = 256
        mock.netmask = ipaddress.IPv4Address('255.255.255.0')
        # Create a list of 5 mock IP addresses for the hosts method
        mock_hosts = [
            ipaddress.IPv4Address('192.168.1.1'),
            ipaddress.IPv4Address('192.168.1.2'),
            ipaddress.IPv4Address('192.168.1.3'),
            ipaddress.IPv4Address('192.168.1.4'),
            ipaddress.IPv4Address('192.168.1.5')
        ]
        mock.hosts.return_value = mock_hosts
        return mock

    @patch('ipaddress.ip_network')
    def test_analyze_valid_subnet(self, mock_ip_network, mock_network, mock_console):
        """Test analyzing a valid subnet."""
        # Arrange
        mock_ip_network.return_value = mock_network
        ip_address = '192.168.1.0'
        mask = '24'
        expected_result = {
            'network_address': '192.168.1.0',
            'broadcast_address': '192.168.1.255',
            'num_addresses': 256,
            'netmask': '255.255.255.0',
            'hosts': ['192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4', '192.168.1.5']
        }
        
        # Act
        result = analyze_subnet(ip_address, mask)
        
        # Assert
        assert result == expected_result
        mock_ip_network.assert_called_once_with(f"{ip_address}/{mask}", strict=False)
        assert mock_console.print.call_count >= 4  # At least 4 console print calls expected

    @patch('ipaddress.ip_network')
    def test_analyze_invalid_subnet(self, mock_ip_network, mock_console):
        """Test handling of an invalid subnet."""
        # Arrange
        mock_ip_network.side_effect = ValueError("Invalid IP address")
        ip_address = '192.168.1'  # Invalid IP (missing octet)
        mask = '24'
        
        # Act
        result = analyze_subnet(ip_address, mask)
        
        # Assert
        assert result is None
        mock_ip_network.assert_called_once_with(f"{ip_address}/{mask}", strict=False)
        mock_console.print.assert_called_with("[bold red]Error:[/bold red] Invalid IP address or mask - Invalid IP address")

    @patch('builtins.input')
    @patch('ipaddress.ip_network')
    def test_analyze_with_user_input(self, mock_ip_network, mock_input, mock_network, mock_console):
        """Test subnet analysis with user input for IP address and mask."""
        # Arrange
        mock_ip_network.return_value = mock_network
        mock_input.side_effect = ['10.0.0.0', '8']
        
        # Act
        result = analyze_subnet()
        
        # Assert
        assert result is not None
        assert result['network_address'] == '192.168.1.0'  # from mock_network
        mock_input.assert_called()
        assert mock_input.call_count == 2
        mock_ip_network.assert_called_once_with("10.0.0.0/8", strict=False)


class TestPing:
    """Test cases for the ping function."""

    @pytest.fixture
    def mock_process(self):
        """Create a mock subprocess.Popen for testing."""
        mock = MagicMock()
        mock.returncode = 0
        mock.communicate.return_value = (
            b"""
            Ping statistics for 8.8.8.8:
                Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
            Approximate round trip times in milli-seconds:
                Minimum = 20ms, Maximum = 35ms, Average = 25ms
            """,
            b""
        )
        return mock

    @patch('platform.system')
    @patch('subprocess.Popen')
    @patch('time.time')
    def test_ping_successful_windows(self, mock_time, mock_popen, mock_platform, mock_process, mock_console):
        """Test successful ping on Windows platform."""
        # Arrange
        mock_platform.return_value = 'Windows'
        mock_popen.return_value = mock_process
        mock_time.side_effect = [0, 1]  # Start time, end time
        target = '8.8.8.8'
        count = 4
        
        expected_stats = {
            'packets_sent': 4,
            'packets_received': 4,
            'loss_percentage': 0,
            'min_time': 20,
            'max_time': 35,
            'avg_time': 25,
            'total_time': 1.0
        }
        
        # Act
        result = ping(target, count)
        
        # Assert
        assert isinstance(result, dict)
        assert result == expected_stats
        mock_popen.assert_called_once()
        mock_platform.assert_called()

    @patch('platform.system')
    @patch('subprocess.Popen')
    def test_ping_failed(self, mock_popen, mock_platform, mock_console):
        """Test failed ping where the command returns non-zero."""
        # Arrange
        mock_platform.return_value = 'Linux'
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"", b"Error: Host unreachable")
        mock_popen.return_value = mock_process
        target = 'unreachable-host'
        count = 2
        
        # Act
        result = ping(target, count)
        
        # Assert
        assert result is None
        mock_popen.assert_called_once()
        mock_console.print.assert_called_with(f"[bold red]Error:[/bold red] Failed to ping {target}")

    @patch('platform.system')
    @patch('subprocess.Popen')
    @patch('time.time')
    def test_ping_successful_linux(self, mock_time, mock_popen, mock_platform, mock_console):
        """Test successful ping on Linux/Unix platform."""
        # Arrange
        mock_platform.return_value = 'Linux'
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (
            b"""
            PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
            64 bytes from 8.8.8.8: icmp_seq=1 ttl=118 time=15.5 ms
            64 bytes from 8.8.8.8: icmp_seq=2 ttl=118 time=14.2 ms
            
            --- 8.8.8.8 ping statistics ---
            2 packets transmitted, 2 received, 0% packet loss, time 1001ms
            rtt min/avg/max/mdev = 14.222/14.884/15.546/0.662 ms
            """,
            b""
        )
        mock_popen.return_value = mock_process
        mock_time.side_effect = [0, 1.5]  # Start time, end time
        target = '8.8.8.8'
        count = 2
        
        expected_stats = {
            'packets_sent': 2,
            'packets_received': 2,
            'loss_percentage': 0,
            'min_time': 14.222,
            'avg_time': 14.884,
            'max_time': 15.546,
            'total_time': 1.5
        }
        
        # Act
        result = ping(target, count)
        
        # Assert
        assert isinstance(result, dict)
        assert result['packets_sent'] == expected_stats['packets_sent']
        assert result['packets_received'] == expected_stats['packets_received']
        assert result['loss_percentage'] == expected_stats['loss_percentage']
        assert result['min_time'] == expected_stats['min_time']
        mock_popen.assert_called_once()

    @patch('builtins.input')
    @patch('platform.system')
    @patch('subprocess.Popen')
    def test_ping_with_user_input(self, mock_popen, mock_platform, mock_input, mock_console):
        """Test ping with user input for target."""
        # Arrange
        mock_input.return_value = '1.1.1.1'
        mock_platform.return_value = 'Linux'
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (
            b"4 packets transmitted, 4 received, 0% packet loss",
            b""
        )
        mock_popen.return_value = mock_process
        
        # Act
        result = ping()
        
        # Assert
        assert result is not None
        mock_input.assert_called_once()
        mock_popen.assert_called_once()
        assert '1.1.1.1' in mock_popen.call_args[0][0]  # Check if the command includes the input IP