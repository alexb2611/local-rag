# Time-Series RAG Application

A Retrieval-Augmented Generation (RAG) system for querying environmental monitoring CSV data using natural language.

## Features

- **Time-based chunking**: Groups sensor readings into configurable time periods (default 4 hours)
- **Preserves temporal relationships**: Maintains the time-series nature of the data
- **Rich contextual descriptions**: Includes trends, ranges, and summary statistics
- **Multiple data sources**: Load single CSV files or entire directories
- **Dual LLM support**: Choose between Claude Sonnet 4 or local Ollama models
- **MMR search**: Maximum Marginal Relevance search for comprehensive coverage
- **Persistent vector store**: Uses ChromaDB for efficient retrieval

## Installation

### 1. Prerequisites

- Python 3.9 or higher
- Ollama installed and running
- (Optional) Anthropic API key for Claude Sonnet 4

### 2. Install Ollama models

```bash
# Install the embedding model (required)
ollama pull nomic-embed-text

# Install the LLM model (optional - for local processing)
ollama pull granite4:small-h
```

### 3. Install Python dependencies

```bash
# Activate your virtual environment first
source .venv/bin/activate  # On Linux/WSL
# .venv\Scripts\activate  # On Windows

# Install requirements
pip install -r requirements_timeseries.txt
```

### 4. Set up environment variables

Create a `.env` file in the project directory:

```bash
# For Claude Sonnet 4 (optional)
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Running the application

```bash
streamlit run csv_rag_app.py
```

The application will open in your browser at `http://localhost:8501`

### Loading data

#### Option 1: Upload single CSV
1. Select "Upload single CSV" in the sidebar
2. Choose your hours-per-chunk setting (default: 4 hours)
3. Upload a CSV file (e.g., `lora_data_2025-12-02.csv`)
4. Click "Process CSV"

#### Option 2: Load from directory
1. Select "Load from directory" in the sidebar
2. Enter the directory path containing your CSV files
3. Choose your hours-per-chunk setting
4. Click "Load CSV files from directory"

### Expected CSV format

Your CSV files should have the following columns:
- `timestamp`: Time in HH:MM:SS format
- `temperature`: Temperature in °C
- `humidity`: Humidity percentage
- `pressure`: Atmospheric pressure in hPa
- `battery`: Battery voltage
- `charging`: Charging status (0 or 1)
- `interval`: Transmission interval in seconds
- `rssi`: Signal strength in dBm
- `snr`: Signal-to-noise ratio in dB

Filenames should include the date, e.g., `lora_data_2025-12-02.csv`

### Querying the data

Once data is loaded, you can ask questions like:

**Temperature queries:**
- "What was the temperature trend throughout the day?"
- "When was the coldest period?"
- "What was the temperature range during the afternoon?"

**Humidity queries:**
- "What was the average humidity overnight?"
- "When did humidity peak?"

**Pressure queries:**
- "How did atmospheric pressure change during the day?"
- "Was pressure rising or falling in the evening?"

**System queries:**
- "Were there any battery issues?"
- "How was the signal quality?"

**Multi-factor queries:**
- "What were conditions like during the morning?"
- "How did temperature and humidity correlate?"

## Configuration

### Chunking strategy

The application groups sensor readings into time-based chunks. You can adjust the chunk size:

- **1 hour**: Very granular, more chunks, good for detecting short-term changes
- **4 hours**: Default, balanced between detail and overview
- **12 hours**: Larger view, fewer chunks, good for general daily patterns

### Retrieval settings

The application uses Maximum Marginal Relevance (MMR) search:
- `k=15`: Returns 15 chunks
- `fetch_k=30`: Initially retrieves 30 candidates, then selects 15 diverse ones

These settings ensure comprehensive coverage of your data.

## Project structure

```
local-model/
├── csv_rag_app.py              # Main Streamlit application
├── csv_processor.py            # CSV processing and chunking logic
├── requirements_timeseries.txt # Python dependencies
├── .env                        # Environment variables (create this)
├── csv_data/                   # Directory for CSV files (optional)
│   ├── lora_data_2025-12-01.csv
│   ├── lora_data_2025-12-02.csv
│   └── ...
└── chroma_db_timeseries/      # Vector store (created automatically)
```

## How it works

### 1. Data Processing

The application processes CSV files in several steps:

1. **Load CSV**: Reads the file and parses timestamps
2. **Time grouping**: Groups readings into configurable time blocks (e.g., 4-hour periods)
3. **Statistical analysis**: Calculates min/max/average for each metric
4. **Trend detection**: Determines if values are increasing or decreasing
5. **Text generation**: Creates rich textual descriptions suitable for embedding
6. **Metadata**: Stores temporal information for filtering and source attribution

### 2. Chunking Strategy

Unlike traditional RAG that splits text by character count, this application uses time-based chunking:

```python
# Traditional approach (bad for time-series)
chunks = text_splitter.split_text(csv_content)

# Time-based approach (good for time-series)
chunks = group_by_time_period(dataframe, hours=4)
```

This preserves temporal relationships and creates semantically meaningful chunks.

### 3. Retrieval

The application uses Maximum Marginal Relevance (MMR) to retrieve diverse, relevant chunks:

- Finds chunks semantically similar to your query
- Ensures diversity to cover different time periods
- Returns 15 chunks from 30 candidates

### 4. Answer Generation

The LLM receives:
- Your question
- 15 relevant time-period summaries with statistics and trends
- A custom prompt optimized for time-series analysis

## Comparison with Document RAG

**Document RAG** (original app.py):
- Best for: PDFs, documents, text content
- Chunking: Character-based splitting
- Use case: "What does the manual say about X?"

**Time-Series RAG** (this application):
- Best for: CSV data, sensor readings, time-series
- Chunking: Time-based grouping
- Use case: "What was the temperature trend during the morning?"

Both applications can coexist - use the one that fits your data type.

## Troubleshooting

### Ollama connection issues

```bash
# Check if Ollama is running
curl http://localhost:11434

# Check available models
ollama list

# Pull missing models
ollama pull nomic-embed-text
```

### Empty or incorrect results

- Check your CSV format matches the expected columns
- Try adjusting the hours-per-chunk setting
- Ensure your question relates to the time period in your data
- Check the "Source Data" section to see what was retrieved

### Memory issues with large datasets

- Reduce hours-per-chunk to create smaller chunks
- Process files individually rather than loading entire directories
- Consider filtering to date ranges of interest

## Future Enhancements

Potential improvements for this application:

- Multi-day trend analysis
- Anomaly detection
- Data visualisation of retrieved periods
- Export query results
- Comparative analysis between different dates
- Support for additional CSV formats

## Contributing

Feel free to modify the code to suit your specific sensor data format or use case.

## License

This is a learning/example project - use as you wish.
