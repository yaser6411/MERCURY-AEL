"""Pytest configuration and shared fixtures for MERCURY-AEL tests."""
import pytest
import tempfile
import os
from pathlib import Path

@pytest.fixture
def temp_project_dir():
    """Create temporary project directory for testing."""
    with tempfile.TemporaryDirectory(prefix='mercury_test_') as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_python_candidate():
    """Sample Python candidate algorithm for testing."""
    return '''
def bubble_sort(arr):
    """Simple bubble sort implementation."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
'''

@pytest.fixture
def sample_invalid_candidate():
    """Invalid Python candidate with syntax error."""
    return '''
def broken_function(
    return None  # Missing closing paren
'''

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        'policies': {
            'verification_cycles': 10,
            'minimum_score': 0.80,
            'gates': {
                'syntax': 'required',
                'compilation': 'required',
                'unit_tests': 'required',
                'property_tests': 'required',
                'edge_tests': 'required',
                'security_checks': 'required',
                'resource_limits': 'required',
                'benchmark': 'required'
            },
            'scoring_weights': {
                'correctness': 0.40,
                'edge_coverage': 0.15,
                'performance': 0.20,
                'security': 0.15,
                'efficiency': 0.10
            }
        },
        'limits': {
            'max_ram_mb': 2048,
            'max_cpu_percent': 50,
            'max_cpu_time_sec': 300,
            'max_disk_mb': 5120,
            'max_generations': 100,
            'max_candidate_size_kb': 512,
            'max_execution_time_sec': 3600,
            'sandbox_timeout_sec': 60
        }
    }

@pytest.fixture
def mock_hardware():
    """Mock hardware profile for testing."""
    return {
        'cpu_architecture': 'x86_64',
        'cpu_count': 8,
        'ram_mb': 16384,
        'disk_mb': 500000,
        'os': 'Linux',
        'kernel_version': '5.15.0',
        'available_compilers': ['gcc', 'clang'],
        'available_runtimes': ['python3']
    }
