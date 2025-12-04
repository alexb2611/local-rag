"""
Configuration file for available LLM models.

To add a new model:
1. Add an entry to the MODELS list below
2. Set the 'provider' to either 'ollama', 'anthropic', or add a new provider
3. If adding a new provider, update the get_model_and_embeddings function in app.py

Model configuration fields:
- name: The model identifier (used in API calls)
- display_name: Human-readable name shown in the UI
- provider: 'ollama' or 'anthropic' (or custom provider)
- description: Optional description of the model
"""

MODELS = [
    {
        "name": "granite4:small-h",
        "display_name": "Granite 4 Small (Local)",
        "provider": "ollama",
        "description": "Balanced performance, runs locally via Ollama"
    },
    {
        "name": "granite4:tiny-h",
        "display_name": "Granite 4 Tiny (Local)",
        "provider": "ollama",
        "description": "Smaller and faster, runs locally via Ollama"
    },
    {
        "name": "claude-sonnet-4-20250514",
        "display_name": "Claude Sonnet 4",
        "provider": "anthropic",
        "description": "Anthropic's Claude Sonnet 4 (requires API key)"
    },
    # Add more models below:
    # {
    #     "name": "llama3.2:latest",
    #     "display_name": "Llama 3.2 (Local)",
    #     "provider": "ollama",
    #     "description": "Meta's Llama 3.2 model"
    # },
    # {
    #     "name": "mistral:latest",
    #     "display_name": "Mistral (Local)",
    #     "provider": "ollama",
    #     "description": "Mistral AI model"
    # },
    # {
    #     "name": "claude-opus-4-20250514",
    #     "display_name": "Claude Opus 4",
    #     "provider": "anthropic",
    #     "description": "Anthropic's most capable model (requires API key)"
    # },
]

# Embedding model configuration
EMBEDDING_MODEL = {
    "name": "nomic-embed-text",
    "provider": "ollama"
}

def get_model_list():
    """Returns list of model names for the dropdown"""
    return [model["name"] for model in MODELS]

def get_model_display_names():
    """Returns dict mapping model names to display names"""
    return {model["name"]: model["display_name"] for model in MODELS}

def get_model_config(model_name):
    """Get configuration for a specific model"""
    for model in MODELS:
        if model["name"] == model_name:
            return model
    return None

def get_default_model():
    """Returns the default model name"""
    return MODELS[0]["name"] if MODELS else None
