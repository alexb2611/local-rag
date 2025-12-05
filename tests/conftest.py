"""Pytest configuration and shared fixtures"""
import os
import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime, date
import tempfile
import shutil


@pytest.fixture
def sample_csv_data():
    """Sample CSV data matching the LoRa sensor format"""
    data = {
        'timestamp': [
            '00:00:00', '01:00:00', '02:00:00', '03:00:00', '04:00:00',
            '05:00:00', '06:00:00', '07:00:00', '08:00:00', '09:00:00',
            '10:00:00', '11:00:00', '12:00:00'
        ],
        'temperature': [18.5, 18.2, 18.0, 17.8, 17.9, 18.1, 18.5, 19.2, 20.1, 21.3, 22.5, 23.1, 23.8],
        'humidity': [65.0, 66.0, 67.0, 68.0, 67.5, 66.5, 65.0, 63.0, 60.0, 58.0, 55.0, 53.0, 52.0],
        'pressure': [1013.2, 1013.1, 1013.0, 1012.9, 1012.8, 1012.7, 1012.8, 1013.0, 1013.2, 1013.5, 1013.8, 1014.0, 1014.2],
        'battery': [4.18, 4.17, 4.16, 4.15, 4.14, 4.13, 4.12, 4.15, 4.18, 4.19, 4.20, 4.21, 4.22],
        'charging': [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        'rssi': [-85, -87, -86, -85, -88, -86, -84, -83, -82, -81, -80, -79, -78],
        'snr': [8.5, 8.2, 8.0, 7.8, 7.5, 7.8, 8.0, 8.3, 8.5, 8.8, 9.0, 9.2, 9.5],
        'interval': [600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_csv_file(tmp_path, sample_csv_data):
    """Create a temporary CSV file with sample data"""
    csv_path = tmp_path / "lora_data_2025-12-02.csv"
    sample_csv_data.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def sample_csv_file_no_date(tmp_path, sample_csv_data):
    """Create a CSV file without date in filename"""
    csv_path = tmp_path / "sensor_data.csv"
    sample_csv_data.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def empty_csv_file(tmp_path):
    """Create an empty CSV file"""
    csv_path = tmp_path / "empty.csv"
    df = pd.DataFrame()
    df.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def malformed_csv_file(tmp_path):
    """Create a CSV file with missing required columns"""
    csv_path = tmp_path / "malformed.csv"
    df = pd.DataFrame({
        'timestamp': ['00:00:00', '01:00:00'],
        'temperature': [20.0, 21.0]
        # Missing other required columns
    })
    df.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def multiple_csv_directory(tmp_path, sample_csv_data):
    """Create directory with multiple CSV files"""
    # Create 3 CSV files with different dates
    dates = ['2025-12-01', '2025-12-02', '2025-12-03']
    for date_str in dates:
        csv_path = tmp_path / f"lora_data_{date_str}.csv"
        sample_csv_data.to_csv(csv_path, index=False)

    # Add a non-CSV file
    (tmp_path / "readme.txt").write_text("This is not a CSV file")

    return str(tmp_path)


@pytest.fixture
def temp_chroma_dir(tmp_path):
    """Create a temporary ChromaDB directory"""
    chroma_dir = tmp_path / "test_chroma_db"
    chroma_dir.mkdir()
    return str(chroma_dir)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key-12345")
    return {"ANTHROPIC_API_KEY": "test-api-key-12345"}


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing"""
    return """# Test Document

## Introduction
This is a test markdown document for testing purposes.

## Section 1
Lorem ipsum dolor sit amet, consectetur adipiscing elit.

## Section 2
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
"""


@pytest.fixture
def sample_markdown_file(tmp_path, sample_markdown_content):
    """Create a temporary markdown file"""
    md_path = tmp_path / "test_document.md"
    md_path.write_text(sample_markdown_content)
    return str(md_path)


@pytest.fixture
def freeze_time():
    """Fixture to freeze time for testing"""
    from freezegun import freeze_time as _freeze_time
    with _freeze_time("2025-12-05"):
        yield
