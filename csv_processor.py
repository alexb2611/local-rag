"""
CSV Time-Series Processor for RAG
Handles loading and chunking of environmental monitoring CSV data
"""

import pandas as pd
import re
from langchain_core.documents import Document
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional


def create_time_based_chunks(
    csv_path: str, 
    date_str: Optional[str] = None,
    hours_per_chunk: int = 4
) -> List[Document]:
    """
    Create time-based chunks from CSV data.
    
    Args:
        csv_path: Path to CSV file
        date_str: Date string in format 'YYYY-MM-DD'. If None, extracted from filename
        hours_per_chunk: Number of hours per chunk (default 4)
        
    Returns:
        List of Document objects with rich textual descriptions
    """
    # Extract date from filename if not provided
    if date_str is None:
        # Assumes filename like 'lora_data_2025-12-02.csv'
        filename = Path(csv_path).stem  # Gets filename without extension
        # Try to find a date pattern in the filename
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if date_match:
            date_str = date_match.group(1)
        else:
            # Fallback: use current date
            date_str = date.today().strftime('%Y-%m-%d')
            print(f"Warning: Could not extract date from filename '{filename}', using today's date: {date_str}")
    
    # Ensure date_str is a string
    date_str = str(date_str)
    
    # Load CSV
    df = pd.read_csv(csv_path)
    
    # Add full datetime column - combine date and time properly
    # The timestamp column is in HH:MM:SS format
    df['datetime'] = df['timestamp'].apply(lambda t: pd.to_datetime(f"{date_str} {t}"))
    df['hour'] = df['datetime'].dt.hour
    
    # Group into time blocks
    df['time_block'] = (df['hour'] // hours_per_chunk)
    
    chunks = []
    for block, group in df.groupby('time_block'):
        start_time = group['datetime'].min()
        end_time = group['datetime'].max()
        
        # Calculate trends
        temp_trend = "increasing" if group['temperature'].iloc[-1] > group['temperature'].iloc[0] else "decreasing"
        humid_trend = "increasing" if group['humidity'].iloc[-1] > group['humidity'].iloc[0] else "decreasing"
        pressure_trend = "increasing" if group['pressure'].iloc[-1] > group['pressure'].iloc[0] else "decreasing"
        
        # Create rich textual description
        content = f"""Environmental Monitoring Data

Date: {date_str}
Time period: {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}

TEMPERATURE:
- Minimum: {group['temperature'].min():.2f}°C
- Maximum: {group['temperature'].max():.2f}°C
- Average: {group['temperature'].mean():.2f}°C
- Trend: {temp_trend}
- Range: {group['temperature'].max() - group['temperature'].min():.2f}°C

HUMIDITY:
- Minimum: {group['humidity'].min():.1f}%
- Maximum: {group['humidity'].max():.1f}%
- Average: {group['humidity'].mean():.1f}%
- Trend: {humid_trend}

PRESSURE:
- Minimum: {group['pressure'].min():.2f} hPa
- Maximum: {group['pressure'].max():.2f} hPa
- Average: {group['pressure'].mean():.2f} hPa
- Trend: {pressure_trend}

SYSTEM STATUS:
- Battery voltage: {group['battery'].mean():.2f}V
- Charging: {"Yes" if group['charging'].mean() > 0.5 else "No"}
- Average signal strength (RSSI): {group['rssi'].mean():.1f} dBm
- Average signal-to-noise ratio (SNR): {group['snr'].mean():.2f} dB
- Transmission interval: {group['interval'].mode()[0]} seconds

DATA QUALITY:
- Number of readings: {len(group)}
- Time coverage: {(end_time - start_time).total_seconds() / 3600:.1f} hours
"""
        
        chunks.append(Document(
            page_content=content,
            metadata={
                "date": date_str,
                "start_time": str(start_time),
                "end_time": str(end_time),
                "time_block": f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
                "source": str(csv_path),
                "readings_count": len(group),
                "avg_temperature": float(group['temperature'].mean()),
                "avg_humidity": float(group['humidity'].mean()),
                "avg_pressure": float(group['pressure'].mean()),
            }
        ))
    
    return chunks


def load_multiple_csv_files(
    directory: str,
    pattern: str = "*.csv",
    hours_per_chunk: int = 4
) -> List[Document]:
    """
    Load multiple CSV files from a directory.
    
    Args:
        directory: Directory containing CSV files
        pattern: File pattern to match (default "*.csv")
        hours_per_chunk: Number of hours per chunk
        
    Returns:
        List of all Document chunks from all files
    """
    from pathlib import Path
    
    directory_path = Path(directory)
    all_chunks = []
    
    csv_files = sorted(directory_path.glob(pattern))
    
    for csv_file in csv_files:
        print(f"Processing {csv_file.name}...")
        chunks = create_time_based_chunks(
            str(csv_file), 
            hours_per_chunk=hours_per_chunk
        )
        all_chunks.extend(chunks)
    
    print(f"\nTotal: Processed {len(csv_files)} files into {len(all_chunks)} chunks")
    return all_chunks


def get_data_summary(documents: List[Document]) -> str:
    """
    Generate a summary of the loaded data.
    
    Args:
        documents: List of Document objects
        
    Returns:
        String summary of the dataset
    """
    if not documents:
        return "No data loaded"
    
    dates = set(doc.metadata['date'] for doc in documents)
    total_readings = sum(doc.metadata['readings_count'] for doc in documents)
    
    temps = [doc.metadata['avg_temperature'] for doc in documents]
    humids = [doc.metadata['avg_humidity'] for doc in documents]
    pressures = [doc.metadata['avg_pressure'] for doc in documents]
    
    summary = f"""Dataset Summary:
    
Date range: {min(dates)} to {max(dates)}
Total time periods: {len(documents)}
Total sensor readings: {total_readings}

Overall Statistics:
- Temperature: {min(temps):.1f}°C to {max(temps):.1f}°C
- Humidity: {min(humids):.1f}% to {max(humids):.1f}%
- Pressure: {min(pressures):.1f} hPa to {max(pressures):.1f} hPa
"""
    
    return summary
