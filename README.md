# Document Q&A Assistant

A Streamlit application that allows you to upload PDF and Markdown documents and ask questions about their content using RAG (Retrieval-Augmented Generation).

## Features

- Upload PDF and Markdown documents through a web interface
- Support for multiple document upload and management
- Persistent storage using ChromaDB (documents are retained between sessions)
- Select which documents to search or search across all indexed documents
- Automatic document processing and indexing
- Interactive chat interface for asking questions
- Support for multiple models (Ollama local models and Claude)
- Vector-based document retrieval for accurate answers with source citations
- View page numbers and source excerpts for retrieved information
- Clear database functionality to remove all indexed documents
- Clear chat history option
- Support for image-based PDFs using PyMuPDF fallback

## Prerequisites

- Python 3.8+
- Ollama installed and running (for local models)
- Optional: Anthropic API key (for Claude models)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables (optional, for Claude):
Create a `.env` file in the project directory:
```
ANTHROPIC_API_KEY=your_api_key_here
```

3. Make sure Ollama is running and has the required models:
```bash
ollama pull granite4:small-h
ollama pull granite4:tiny-h  # Optional: smaller, faster model
ollama pull nomic-embed-text
```

## Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The application will open in your default web browser (usually at `http://localhost:8501`).

## Usage

1. **Upload Documents**: Click the "Browse files" button and select one or more PDF or Markdown files
2. **Wait for Processing**: The app will load and index your documents (stored persistently)
3. **Select Documents** (optional): Use the sidebar to choose which indexed documents to search
4. **Ask Questions**: Use the chat input at the bottom to ask questions about your documents
5. **View Answers**: The AI will provide answers based on document content with source citations and page numbers
6. **Manage Documents**: Use the sidebar to view all indexed documents or clear the database
7. **Clear Chat**: Click "Clear Chat History" to reset the conversation

## Configuration

### Selecting a Model

You can change the model in the sidebar. The app supports multiple LLM providers:
- **Ollama models** (local): granite4:small-h, granite4:tiny-h, etc.
- **Anthropic models** (API): claude-sonnet-4-20250514 (requires API key)

### Adding New Models

To add new LLMs to the application, edit the `models_config.py` file:

1. Open `models_config.py`
2. Add a new entry to the `MODELS` list:

```python
{
    "name": "llama3.2:latest",  # Model identifier for API calls
    "display_name": "Llama 3.2 (Local)",  # Name shown in UI
    "provider": "ollama",  # 'ollama' or 'anthropic'
    "description": "Meta's Llama 3.2 model"  # Optional description
}
```

3. Save the file and restart the app

**Supported providers:**
- `ollama`: Local models running via Ollama (make sure to pull the model first: `ollama pull model-name`)
- `anthropic`: Claude models (requires ANTHROPIC_API_KEY in .env file)

**Note:** If you want to add a new provider (e.g., OpenAI, Cohere), you'll need to:
1. Install the required LangChain package (e.g., `langchain-openai`)
2. Update the `get_model_and_embeddings()` function in `app.py` to handle the new provider

## Notes

- The application uses persistent ChromaDB storage, so processed documents are retained between sessions
- Use the "Clear Database" button in the sidebar to remove all indexed documents
- Larger documents may take longer to process
- The quality of answers depends on the selected model and the clarity of the document content
- For image-based PDFs, the app will automatically try PyMuPDF as a fallback if the standard loader fails
- PDFs requiring OCR (scanned images with no text layer) are not currently supported
