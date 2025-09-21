"""
Pytest configuration and fixtures for the Agent Investment Platform test suite.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path for imports
project_root = Path(__file__).parent
src_dir = project_root / 'src'
sys.path.insert(0, str(src_dir))

import pytest


@pytest.fixture(scope="session")
def project_root_path():
    """Provide the project root path."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def src_path():
    """Provide the src directory path."""
    return Path(__file__).parent / 'src'


@pytest.fixture(scope="session")
def test_data_path():
    """Provide the test data directory path."""
    return Path(__file__).parent / 'tests' / 'data'


# Configure async test settings
pytest_plugins = ('pytest_asyncio',)
