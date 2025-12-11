"""
CSV Processor for LoRa Environmental Sensor Data
Handles both standard and solar-enhanced CSV formats with robust error handling
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import glob
import os
import warnings

# Try to import LangChain Document for compatibility
try:
    from langchain_core.documents import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain not available - Document conversion will not work")

warnings.filterwarnings('ignore')


def read_mixed_format_csv(csv_path: str) -> Optional[pd.DataFrame]:
    """
    Read CSV file handling multiple sensor formats with robust error handling.
    Automatically extracts date from filename and combines with time-only timestamps.
    
    Standard format (8 fields):
        timestamp, temperature, humidity, pressure, battery, power_source, rssi, snr
    
    Solar format without uptime (9 fields):
        timestamp, temperature, humidity, pressure, battery, charging, interval, rssi, snr
    
    Full solar format (11 fields):
        timestamp, temperature, humidity, pressure, battery, charging, interval, 
        uptime, power_source, rssi, snr
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        DataFrame with normalized columns and proper datetime timestamps, or None if file cannot be read
    """
    # Extract date from filename (e.g., lora_data_2025-12-02.csv)
    file_date = extract_date_from_filename(csv_path)
    
    try:
        # First attempt: normal pandas read with error skipping
        df = pd.read_csv(csv_path, on_bad_lines='skip')
        
        if df is not None and not df.empty:
            # Normalize column names and add missing columns with defaults
            df = normalize_csv_columns(df)
            
            # Combine filename date with time-only timestamps
            df = combine_date_and_time(df, file_date)
            
            return df
            
    except pd.errors.ParserError:
        # Fallback: line-by-line parsing for mixed format files
        print(f"⚠️  Mixed format detected in {csv_path}, using robust parsing...")
        df = parse_mixed_format_line_by_line(csv_path)
        
        if df is not None:
            # Combine filename date with time-only timestamps
            df = combine_date_and_time(df, file_date)
        
        return df
        
    except Exception as e:
        print(f"❌ Error reading {csv_path}: {e}")
        return None


def normalize_csv_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add missing columns with default values and normalize charging values for consistency.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with all expected columns and normalized values
    """
    # Core sensor columns (should always exist)
    required_columns = ['timestamp', 'temperature', 'humidity', 'pressure', 'battery']
    
    for col in required_columns:
        if col not in df.columns:
            print(f"⚠️  Warning: Missing required column '{col}'")
            return pd.DataFrame()  # Return empty if core columns missing
    
    # Optional columns with defaults
    if 'power_source' not in df.columns:
        # If we have charging info, assume Solar, otherwise Unknown
        if 'charging' in df.columns:
            df['power_source'] = 'Solar'
        else:
            df['power_source'] = 'Unknown'
    
    if 'rssi' not in df.columns:
        df['rssi'] = 0
        
    if 'snr' not in df.columns:
        df['snr'] = 0.0
    
    # Solar-specific columns
    if 'charging' not in df.columns:
        df['charging'] = 'N'
    else:
        # Normalize charging values: convert 1/0 or various text formats to Y/N
        df['charging'] = df['charging'].apply(
            lambda x: 'Y' if str(x).strip() in ['1', 'Y', 'y', 'yes', 'Yes', 'YES', 'True', 'true'] else 'N'
        )
        
    if 'interval' not in df.columns:
        df['interval'] = 0
        
    if 'uptime' not in df.columns:
        df['uptime'] = 0
    
    return df


def parse_mixed_format_line_by_line(csv_path: str) -> Optional[pd.DataFrame]:
    """
    Parse CSV files with inconsistent column counts line by line.
    Handles files that contain a mix of standard and solar format rows.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        DataFrame with normalized data, or None if parsing fails
    """
    rows = []
    
    try:
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines):
            # Skip header and empty lines
            if line_num == 0 or not line.strip():
                continue
                
            fields = [f.strip() for f in line.strip().split(',')]
            
            try:
                row_dict = {}
                
                # Core fields (should be present in all formats)
                if len(fields) < 5:
                    continue  # Not enough fields for even basic data
                
                row_dict['timestamp'] = fields[0]
                row_dict['temperature'] = float(fields[1])
                row_dict['humidity'] = float(fields[2])
                row_dict['pressure'] = float(fields[3])
                row_dict['battery'] = float(fields[4])
                
                if len(fields) == 8:  # Standard format
                    row_dict['power_source'] = fields[5]
                    row_dict['rssi'] = int(fields[6])
                    row_dict['snr'] = float(fields[7])
                    # Add solar columns with defaults
                    row_dict['charging'] = 'N'
                    row_dict['interval'] = 0
                    row_dict['uptime'] = 0
                    
                elif len(fields) == 9:  # Solar format without uptime (charging, interval, rssi, snr)
                    # Format: timestamp,temperature,humidity,pressure,battery,charging,interval,rssi,snr
                    row_dict['charging'] = 'Y' if fields[5].strip() in ['1', 'Y', 'y', 'yes', 'Yes'] else 'N'
                    row_dict['interval'] = int(fields[6]) if fields[6].strip() else 0
                    row_dict['rssi'] = int(fields[7])
                    row_dict['snr'] = float(fields[8])
                    # Add missing columns with defaults
                    row_dict['power_source'] = 'Solar'
                    row_dict['uptime'] = 0
                    
                elif len(fields) >= 11:  # Full solar format with uptime
                    row_dict['charging'] = fields[5]
                    row_dict['interval'] = int(fields[6]) if fields[6] else 0
                    row_dict['uptime'] = int(fields[7]) if fields[7] else 0
                    row_dict['power_source'] = fields[8]
                    row_dict['rssi'] = int(fields[9])
                    row_dict['snr'] = float(fields[10])
                    
                else:
                    # Unexpected format - try to handle partial data
                    if len(fields) >= 6:
                        row_dict['power_source'] = fields[5]
                    else:
                        row_dict['power_source'] = 'Unknown'
                    
                    # Fill remaining with defaults
                    for key in ['rssi', 'snr', 'interval', 'uptime']:
                        if key not in row_dict:
                            row_dict[key] = 0
                    if 'charging' not in row_dict:
                        row_dict['charging'] = 'N'
                
                rows.append(row_dict)
                
            except (ValueError, IndexError) as e:
                # Skip malformed rows silently
                print(f"⚠️  Skipping malformed row {line_num + 1}: {e}")
                continue
        
        if rows:
            return pd.DataFrame(rows)
        else:
            print(f"❌ No valid data rows found in {csv_path}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to parse {csv_path} with robust method: {e}")
        return None


def extract_date_from_filename(filepath: str) -> Optional[str]:
    """
    Extract date from filename in format: lora_data_YYYY-MM-DD.csv
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        Date string in YYYY-MM-DD format, or None if not found
    """
    import re
    filename = os.path.basename(filepath)
    # Pattern: lora_data_2025-12-02.csv
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        return match.group(0)  # Returns YYYY-MM-DD
    return None


def combine_date_and_time(df: pd.DataFrame, date_str: Optional[str]) -> pd.DataFrame:
    """
    Combine date from filename with time-only timestamps in DataFrame.
    
    Args:
        df: DataFrame with 'timestamp' column containing time-only strings (HH:MM:SS)
        date_str: Date string in YYYY-MM-DD format from filename
        
    Returns:
        DataFrame with 'timestamp' column as proper datetime objects
    """
    if date_str is None:
        # Fallback to parsing as time-only (will use 1900-01-01 as date)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%H:%M:%S', errors='coerce')
    else:
        # Combine date with time
        # Create datetime strings like "2025-12-02 12:34:56"
        df['timestamp'] = date_str + ' ' + df['timestamp'].astype(str)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    
    return df


def detect_solar_data(df: pd.DataFrame) -> Tuple[bool, Dict]:
    """
    Detect if DataFrame contains solar sensor data and return solar statistics.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple of (has_solar: bool, solar_info: dict)
    """
    if df.empty:
        return False, {}
    
    # Check if we have any actual solar data (not just default values)
    has_solar = (df['charging'] != 'N').any() or \
                (df['interval'] > 0).any() or \
                (df['uptime'] > 0).any()
    
    if has_solar:
        solar_info = {
            'charging_percentage': (df['charging'] == 'Y').sum() / len(df) * 100,
            'avg_interval': df['interval'].mean(),
            'max_uptime': df['uptime'].max(),
            'avg_uptime': df['uptime'].mean()
        }
        return True, solar_info
    
    return False, {}


def chunk_csv_data(df: pd.DataFrame, hours_per_chunk: int = 24) -> List[pd.DataFrame]:
    """
    Split CSV data into time-based chunks.
    
    Args:
        df: Input DataFrame with timestamp column
        hours_per_chunk: Hours of data per chunk (default 24 for daily chunks)
        
    Returns:
        List of DataFrame chunks
    """
    if df.empty:
        return []
    
    # Timestamps should already be datetime objects from read_mixed_format_csv
    # Just verify they are datetime type
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        print("⚠️  Warning: timestamp column is not datetime type, attempting conversion")
        # Try generic conversion (will preserve date if already combined)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Remove any rows with invalid timestamps
    df = df.dropna(subset=['timestamp'])
    
    if df.empty:
        return []
    
    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Calculate time differences
    df['time_diff'] = df['timestamp'].diff()
    
    # Split into chunks based on time gaps or chunk size
    chunks = []
    chunk_start = 0
    current_duration = timedelta(0)
    max_duration = timedelta(hours=hours_per_chunk)
    
    for i in range(1, len(df)):
        time_diff = df.loc[i, 'time_diff']
        
        # Check for large time gap (more than 1 hour) indicating a new day or restart
        if pd.notna(time_diff) and time_diff > timedelta(hours=1):
            # Save current chunk
            chunks.append(df.iloc[chunk_start:i].copy())
            chunk_start = i
            current_duration = timedelta(0)
        else:
            # Add to current duration
            if pd.notna(time_diff):
                current_duration += time_diff
            
            # Check if we've reached the chunk duration limit
            if current_duration >= max_duration:
                chunks.append(df.iloc[chunk_start:i].copy())
                chunk_start = i
                current_duration = timedelta(0)
    
    # Add the last chunk
    if chunk_start < len(df):
        chunks.append(df.iloc[chunk_start:].copy())
    
    return [chunk for chunk in chunks if not chunk.empty]


def calculate_statistics(group: pd.DataFrame) -> Dict:
    """
    Calculate comprehensive statistics for a data chunk.
    
    Args:
        group: DataFrame chunk
        
    Returns:
        Dictionary of statistics
    """
    stats = {
        'count': len(group),
        'time_start': group['timestamp'].iloc[0],
        'time_end': group['timestamp'].iloc[-1],
    }
    
    # Environmental statistics
    for param in ['temperature', 'humidity', 'pressure']:
        if param in group.columns:
            stats[f'{param}_min'] = group[param].min()
            stats[f'{param}_max'] = group[param].max()
            stats[f'{param}_mean'] = group[param].mean()
            stats[f'{param}_std'] = group[param].std()
    
    # Battery statistics
    if 'battery' in group.columns:
        stats['battery_min'] = group['battery'].min()
        stats['battery_max'] = group['battery'].max()
        stats['battery_mean'] = group['battery'].mean()
    
    # Signal quality
    if 'rssi' in group.columns and group['rssi'].max() != 0:
        stats['rssi_mean'] = group['rssi'].mean()
        stats['rssi_min'] = group['rssi'].min()
    
    if 'snr' in group.columns and group['snr'].max() != 0:
        stats['snr_mean'] = group['snr'].mean()
        stats['snr_min'] = group['snr'].min()
    
    # Solar statistics
    has_solar, solar_info = detect_solar_data(group)
    if has_solar:
        stats['solar_charging_pct'] = solar_info['charging_percentage']
        stats['solar_avg_interval'] = solar_info['avg_interval']
        stats['solar_max_uptime'] = solar_info['max_uptime']
    
    return stats


def generate_chunk_description(group: pd.DataFrame) -> str:
    """
    Generate rich text description for a data chunk.
    Includes environmental data, system status, and solar info if available.
    
    Args:
        group: DataFrame chunk
        
    Returns:
        Formatted text description
    """
    if group.empty:
        return "Empty data chunk"
    
    # Detect solar data
    has_solar, solar_info = detect_solar_data(group)
    
    description = []
    
    # TEMPORAL INFO
    time_start = group['timestamp'].iloc[0]
    time_end = group['timestamp'].iloc[-1]
    
    # Format timestamps with FULL date and time
    if isinstance(time_start, pd.Timestamp):
        # Include full date: "2025-08-15 12:30:00"
        time_start_str = time_start.strftime('%Y-%m-%d %H:%M:%S')
        time_end_str = time_end.strftime('%Y-%m-%d %H:%M:%S')
        # Extract just the date for display
        date_str = time_start.strftime('%Y-%m-%d')
        # Extract month name for easy reference
        month_name = time_start.strftime('%B %Y')  # e.g., "August 2025"
    else:
        time_start_str = str(time_start)
        time_end_str = str(time_end)
        date_str = "Unknown date"
        month_name = "Unknown month"
    
    description.append(f"=== TEMPORAL INFO ===")
    description.append(f"Date: {date_str}")
    description.append(f"Month: {month_name}")
    description.append(f"Time Period: {time_start_str} to {time_end_str}")
    description.append(f"Number of Readings: {len(group)}")
    description.append("")
    
    # ENVIRONMENTAL MEASUREMENTS
    description.append(f"=== ENVIRONMENTAL CONDITIONS ===")
    
    description.append(f"Temperature: "
                      f"min={group['temperature'].min():.1f}°C, "
                      f"max={group['temperature'].max():.1f}°C, "
                      f"avg={group['temperature'].mean():.1f}°C, "
                      f"std={group['temperature'].std():.2f}°C")
    
    description.append(f"Humidity: "
                      f"min={group['humidity'].min():.1f}%, "
                      f"max={group['humidity'].max():.1f}%, "
                      f"avg={group['humidity'].mean():.1f}%, "
                      f"std={group['humidity'].std():.2f}%")
    
    description.append(f"Pressure: "
                      f"min={group['pressure'].min():.0f}hPa, "
                      f"max={group['pressure'].max():.0f}hPa, "
                      f"avg={group['pressure'].mean():.0f}hPa, "
                      f"std={group['pressure'].std():.2f}hPa")
    
    # Detect trends
    temp_trend = "increasing" if group['temperature'].iloc[-1] > group['temperature'].iloc[0] else "decreasing"
    humid_trend = "increasing" if group['humidity'].iloc[-1] > group['humidity'].iloc[0] else "decreasing"
    
    description.append(f"\nTrends: Temperature {temp_trend}, Humidity {humid_trend}")
    description.append("")
    
    # SYSTEM STATUS
    description.append(f"=== SYSTEM STATUS ===")
    
    description.append(f"Battery Voltage: "
                      f"min={group['battery'].min():.2f}V, "
                      f"max={group['battery'].max():.2f}V, "
                      f"avg={group['battery'].mean():.2f}V")
    
    # Battery health assessment
    avg_battery = group['battery'].mean()
    if avg_battery > 3.8:
        battery_health = "Excellent"
    elif avg_battery > 3.6:
        battery_health = "Good"
    elif avg_battery > 3.3:
        battery_health = "Low"
    else:
        battery_health = "Critical"
    
    description.append(f"Battery Health: {battery_health}")
    
    # Power source distribution
    if 'power_source' in group.columns:
        power_sources = group['power_source'].value_counts().to_dict()
        description.append(f"Power Sources: {', '.join([f'{k}({v})' for k, v in power_sources.items()])}")
    
    description.append("")
    
    # SOLAR-SPECIFIC INFO
    if has_solar:
        description.append(f"=== SOLAR SYSTEM INFO ===")
        description.append(f"☀️ Solar-powered sensor detected")
        description.append(f"Charging Status: Active {solar_info['charging_percentage']:.1f}% of time")
        
        if solar_info['avg_interval'] > 0:
            interval_minutes = solar_info['avg_interval'] / 60
            description.append(f"Average Transmission Interval: {interval_minutes:.1f} minutes")
        
        if solar_info['max_uptime'] > 0:
            uptime_hours = solar_info['max_uptime'] / 3600
            description.append(f"Maximum Uptime: {uptime_hours:.2f} hours")
        
        # Solar performance assessment
        if solar_info['charging_percentage'] > 50:
            solar_performance = "Excellent - frequently charging"
        elif solar_info['charging_percentage'] > 25:
            solar_performance = "Good - regular charging"
        elif solar_info['charging_percentage'] > 10:
            solar_performance = "Fair - occasional charging"
        else:
            solar_performance = "Poor - rarely charging"
        
        description.append(f"Solar Performance: {solar_performance}")
        description.append("")
    
    # SIGNAL QUALITY
    if 'rssi' in group.columns and group['rssi'].max() != 0:
        description.append(f"=== SIGNAL QUALITY ===")
        description.append(f"RSSI (Signal Strength): "
                          f"avg={group['rssi'].mean():.0f}dBm, "
                          f"min={group['rssi'].min():.0f}dBm, "
                          f"max={group['rssi'].max():.0f}dBm")
        
        if 'snr' in group.columns and group['snr'].max() != 0:
            description.append(f"SNR (Signal-to-Noise): "
                              f"avg={group['snr'].mean():.1f}dB, "
                              f"min={group['snr'].min():.1f}dB")
        
        # Signal quality assessment
        avg_rssi = group['rssi'].mean()
        if avg_rssi > -80:
            signal_quality = "Excellent"
        elif avg_rssi > -100:
            signal_quality = "Good"
        elif avg_rssi > -120:
            signal_quality = "Fair"
        else:
            signal_quality = "Poor"
        
        description.append(f"Overall Signal Quality: {signal_quality}")
    
    return "\n".join(description)


def process_csv_file(csv_path: str, hours_per_chunk: int = 24) -> List[Dict]:
    """
    Process a single CSV file into chunks with descriptions.
    
    Args:
        csv_path: Path to CSV file
        hours_per_chunk: Hours of data per chunk
        
    Returns:
        List of dictionaries containing chunk data and descriptions
    """
    # Read the CSV file
    df = read_mixed_format_csv(csv_path)
    
    if df is None or df.empty:
        print(f"⚠️  No valid data in {csv_path}")
        return []
    
    # Chunk the data
    chunks = chunk_csv_data(df, hours_per_chunk)
    
    if not chunks:
        print(f"⚠️  No chunks created from {csv_path}")
        return []
    
    # Generate descriptions for each chunk
    processed_chunks = []
    
    for i, chunk in enumerate(chunks):
        description = generate_chunk_description(chunk)
        stats = calculate_statistics(chunk)
        
        processed_chunks.append({
            'chunk_id': i,
            'source_file': csv_path,
            'description': description,
            'statistics': stats,
            'raw_data': chunk
        })
    
    print(f"✅ Processed {csv_path}: {len(chunks)} chunks created")
    
    return processed_chunks


def process_multiple_csv_files(file_paths: List[str], hours_per_chunk: int = 24) -> List[Dict]:
    """
    Process multiple CSV files into chunks.
    
    Args:
        file_paths: List of CSV file paths
        hours_per_chunk: Hours of data per chunk
        
    Returns:
        List of all processed chunks from all files
    """
    all_chunks = []
    
    for file_path in file_paths:
        try:
            chunks = process_csv_file(file_path, hours_per_chunk)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            continue
    
    print(f"\n📊 Total: {len(all_chunks)} chunks from {len(file_paths)} files")
    
    return all_chunks


def chunks_to_documents(chunks: List[Dict]) -> List:
    """
    Convert chunk dictionaries to LangChain Document objects.
    
    Args:
        chunks: List of chunk dictionaries from process_csv_file() or process_multiple_csv_files()
        
    Returns:
        List of LangChain Document objects with:
        - page_content: The chunk description
        - metadata: Dict with chunk_id, source_file, statistics, etc.
    """
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("LangChain is required to convert chunks to Documents. Install with: pip install langchain")
    
    documents = []
    
    for chunk in chunks:
        if not isinstance(chunk, dict):
            print(f"⚠️ Skipping non-dict chunk: {type(chunk)}")
            continue
            
        # Extract the description as page_content
        page_content = chunk.get('description', '')
        
        # Build metadata
        metadata = {
            'chunk_id': int(chunk.get('chunk_id', 0)),  # Ensure int
            'source_file': str(chunk.get('source_file', 'unknown')),  # Ensure str
        }
        
        # Add statistics to metadata (flatten for easier access)
        stats = chunk.get('statistics', {})
        if stats:
            # Convert timestamps to strings (Chroma doesn't accept Timestamp objects)
            time_start = stats.get('time_start', '')
            time_end = stats.get('time_end', '')
            
            # Convert pandas Timestamps to strings
            if hasattr(time_start, 'strftime'):
                time_start_str = time_start.strftime('%Y-%m-%d %H:%M:%S')
                date_str = time_start.strftime('%Y-%m-%d')  # Extract date
            else:
                time_start_str = str(time_start)
                date_str = 'Unknown'
                
            if hasattr(time_end, 'strftime'):
                time_end_str = time_end.strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_end_str = str(time_end)
            
            metadata.update({
                'time_start': time_start_str,
                'time_end': time_end_str,
                'start_time': time_start_str,  # Alias for app compatibility
                'end_time': time_end_str,      # Alias for app compatibility
                'date': date_str,              # NEW: Extract date for display
                'reading_count': int(stats.get('reading_count', 0)),
                'temperature_mean': float(stats.get('temperature_mean', 0)),
                'humidity_mean': float(stats.get('humidity_mean', 0)),
                'pressure_mean': float(stats.get('pressure_mean', 0)),
                'battery_mean': float(stats.get('battery_mean', 0)),
            })
        
        # Create Document object
        doc = Document(page_content=page_content, metadata=metadata)
        documents.append(doc)
    
    return documents


def debug_chunk_structure(chunks, max_items: int = 2):
    """
    Debug helper to inspect chunk structure.
    
    Args:
        chunks: The data structure to inspect
        max_items: Maximum number of items to show details for
    """
    print(f"\n🔍 DEBUG: Chunk Structure Analysis")
    print(f"Type: {type(chunks)}")
    print(f"Length: {len(chunks) if hasattr(chunks, '__len__') else 'N/A'}")
    
    if isinstance(chunks, list) and chunks:
        print(f"\nFirst element type: {type(chunks[0])}")
        
        for i, item in enumerate(chunks[:max_items]):
            print(f"\n--- Item {i} ---")
            print(f"Type: {type(item)}")
            
            if isinstance(item, dict):
                print(f"Keys: {list(item.keys())}")
                if 'chunk_id' in item:
                    print(f"Chunk ID: {item['chunk_id']}")
                if 'source_file' in item:
                    print(f"Source: {item['source_file']}")
            elif isinstance(item, list):
                print(f"List length: {len(item)}")
                if item:
                    print(f"First element type: {type(item[0])}")
            else:
                print(f"Value: {str(item)[:100]}")


# Backward compatibility wrappers for existing code
def create_time_based_chunks(df_or_path, hours_per_chunk: int = 24):
    """
    Create time-based chunks and convert to LangChain Documents.
    
    This is the main entry point for csv_rag_app.py. It handles the full pipeline:
    1. Read CSV file (if filepath provided)
    2. Chunk data by time periods
    3. Generate descriptions and statistics
    4. Convert to LangChain Document objects
    
    Args:
        df_or_path: Either a pandas DataFrame OR a filepath string to CSV file
        hours_per_chunk: Hours of data per chunk (default 24 for daily)
        
    Returns:
        List of LangChain Document objects with page_content and metadata
    """
    # Handle both DataFrame and filepath inputs
    if isinstance(df_or_path, str):
        # It's a filepath - use process_csv_file for full pipeline
        print(f"📖 Reading CSV file: {df_or_path}")
        chunk_dicts = process_csv_file(df_or_path, hours_per_chunk)
        
        if not chunk_dicts:
            print("⚠️  No chunks created from file")
            return []
        
        # Convert to LangChain Documents
        if LANGCHAIN_AVAILABLE:
            documents = chunks_to_documents(chunk_dicts)
            print(f"✅ Created {len(documents)} LangChain Documents")
            return documents
        else:
            print("⚠️  LangChain not available, returning chunk dictionaries")
            return chunk_dicts
            
    elif isinstance(df_or_path, pd.DataFrame):
        # It's already a DataFrame - do the conversion manually
        df = df_or_path
        
        # Chunk the data
        dataframe_chunks = chunk_csv_data(df, hours_per_chunk)
        
        if not dataframe_chunks:
            return []
        
        # Convert DataFrame chunks to dictionaries with descriptions
        chunk_dicts = []
        for i, chunk in enumerate(dataframe_chunks):
            description = generate_chunk_description(chunk)
            stats = calculate_statistics(chunk)
            
            chunk_dicts.append({
                'chunk_id': i,
                'source_file': 'dataframe_input',
                'description': description,
                'statistics': stats,
                'raw_data': chunk
            })
        
        # Convert to LangChain Documents
        if LANGCHAIN_AVAILABLE:
            documents = chunks_to_documents(chunk_dicts)
            return documents
        else:
            return chunk_dicts
            
    else:
        raise TypeError(f"Expected DataFrame or filepath string, got {type(df_or_path)}")


def load_multiple_csv_files(directory_path: str, hours_per_chunk: int = 24, 
                           return_documents: bool = True) -> List:
    """
    Load and process all CSV files matching lora_data_*.csv pattern from a directory.
    
    Args:
        directory_path: Path to directory containing CSV files
        hours_per_chunk: Hours of data per chunk
        return_documents: If True, return LangChain Document objects; if False, return raw dicts
        
    Returns:
        List of LangChain Document objects (or raw dicts if return_documents=False)
        
    Note:
        This function is now consistent with create_time_based_chunks() - returns just the list.
        For summary information, use get_data_summary() on the returned documents.
    """
    # Find all CSV files matching the pattern
    pattern = os.path.join(directory_path, "lora_data_*.csv")
    file_paths = sorted(glob.glob(pattern))
    
    if not file_paths:
        print(f"⚠️  No CSV files found matching pattern: {pattern}")
        return []
    
    print(f"📂 Found {len(file_paths)} CSV files in directory")
    
    # Process all files
    all_chunks = process_multiple_csv_files(file_paths, hours_per_chunk)
    
    # Convert to Documents if requested
    if return_documents and LANGCHAIN_AVAILABLE:
        try:
            result = chunks_to_documents(all_chunks)
            print(f"✅ Converted {len(all_chunks)} chunks to {len(result)} LangChain Documents")
        except Exception as e:
            print(f"⚠️ Failed to convert to Documents: {e}")
            print(f"   Returning raw chunks instead")
            result = all_chunks
    else:
        result = all_chunks
    
    return result


def get_data_summary(chunks) -> str:
    """
    Generate a summary of processed chunks.
    Works with both LangChain Document objects and raw chunk dictionaries.
    
    Args:
        chunks: List of processed chunks (either Documents or dicts)
        
    Returns:
        Summary string
    """
    if not chunks:
        return "No data chunks available"
    
    # Handle case where chunks might be nested or have wrong structure
    if not isinstance(chunks, list):
        return f"Error: Expected list of chunks, got {type(chunks)}"
    
    summary = []
    summary.append(f"=== DATA SUMMARY ===")
    summary.append(f"Total Chunks: {len(chunks)}")
    
    # Detect if we have Documents or dicts
    first_item = chunks[0]
    is_documents = LANGCHAIN_AVAILABLE and hasattr(first_item, 'page_content')
    
    summary.append(f"Format: {'LangChain Documents' if is_documents else 'Raw Dictionaries'}")
    summary.append("")
    
    # Overall statistics
    all_temps = []
    all_humidity = []
    all_pressure = []
    all_battery = []
    time_start = None
    time_end = None
    
    for item in chunks:
        try:
            if is_documents:
                # Extract from Document metadata
                metadata = item.metadata if hasattr(item, 'metadata') else {}
                all_temps.append(metadata.get('temperature_mean', 0))
                all_humidity.append(metadata.get('humidity_mean', 0))
                all_pressure.append(metadata.get('pressure_mean', 0))
                all_battery.append(metadata.get('battery_mean', 0))
                
                if not time_start and 'time_start' in metadata:
                    time_start = metadata['time_start']
                if 'time_end' in metadata:
                    time_end = metadata['time_end']
            else:
                # Extract from dict
                if not isinstance(item, dict) or 'statistics' not in item:
                    continue
                
                stats = item.get('statistics', {})
                if stats:
                    all_temps.append(stats.get('temperature_mean', 0))
                    all_humidity.append(stats.get('humidity_mean', 0))
                    all_pressure.append(stats.get('pressure_mean', 0))
                    all_battery.append(stats.get('battery_mean', 0))
                    
                    if not time_start and 'time_start' in stats:
                        time_start = stats['time_start']
                    if 'time_end' in stats:
                        time_end = stats['time_end']
        except Exception as e:
            print(f"⚠️ Warning: Could not extract stats from item: {e}")
            continue
    
    # Remove zeros (failed extractions)
    all_temps = [t for t in all_temps if t != 0]
    all_humidity = [h for h in all_humidity if h != 0]
    all_pressure = [p for p in all_pressure if p != 0]
    all_battery = [b for b in all_battery if b != 0]
    
    if all_temps:
        summary.append("=== OVERALL STATISTICS ===")
        summary.append(f"Temperature: min={min(all_temps):.1f}°C, max={max(all_temps):.1f}°C, avg={np.mean(all_temps):.1f}°C")
        summary.append(f"Humidity: min={min(all_humidity):.1f}%, max={max(all_humidity):.1f}%, avg={np.mean(all_humidity):.1f}%")
        summary.append(f"Pressure: min={min(all_pressure):.0f}hPa, max={max(all_pressure):.0f}hPa, avg={np.mean(all_pressure):.0f}hPa")
        summary.append(f"Battery: min={min(all_battery):.2f}V, max={max(all_battery):.2f}V, avg={np.mean(all_battery):.2f}V")
    else:
        summary.append("⚠️ No statistics could be extracted")
    
    # Time range
    if time_start and time_end:
        summary.append("")
        summary.append(f"Time Range: {time_start} to {time_end}")
    
    return "\n".join(summary)


# Example usage and testing
if __name__ == "__main__":
    # Test the processor
    print("CSV Processor Module - Ready")
    print("Supports both standard and solar-enhanced LoRa sensor data formats")
    print("\nAvailable functions:")
    print("  - read_mixed_format_csv()")
    print("  - process_csv_file()")
    print("  - process_multiple_csv_files()")
    print("  - chunk_csv_data() / create_time_based_chunks()")
    print("  - load_multiple_csv_files() [backward compatibility]")
    print("  - get_data_summary() [backward compatibility]")
