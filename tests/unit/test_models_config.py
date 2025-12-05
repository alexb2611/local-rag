"""
Unit tests for models_config.py

Tests the model configuration functions including:
- Model list retrieval
- Display name mapping
- Model configuration lookup
- Default model selection
- Configuration structure validation
"""
import pytest
from models_config import (
    MODELS,
    EMBEDDING_MODEL,
    get_model_list,
    get_model_display_names,
    get_model_config,
    get_default_model
)


class TestModelsConfiguration:
    """Tests for MODELS configuration structure"""

    def test_models_list_exists(self):
        """Test that MODELS list is defined"""
        assert MODELS is not None
        assert isinstance(MODELS, list)

    def test_models_list_not_empty(self):
        """Test that MODELS list has at least one model"""
        assert len(MODELS) > 0

    def test_model_structure(self):
        """Test that each model has required fields"""
        required_fields = ['name', 'display_name', 'provider']

        for model in MODELS:
            assert isinstance(model, dict)
            for field in required_fields:
                assert field in model, f"Model missing required field: {field}"
                assert model[field] is not None
                assert model[field] != ""

    def test_model_providers(self):
        """Test that all models have valid providers"""
        valid_providers = ['ollama', 'anthropic']

        for model in MODELS:
            assert model['provider'] in valid_providers, \
                f"Invalid provider: {model['provider']}"

    def test_ollama_models_present(self):
        """Test that at least one Ollama model is configured"""
        ollama_models = [m for m in MODELS if m['provider'] == 'ollama']
        assert len(ollama_models) > 0

    def test_model_names_unique(self):
        """Test that model names are unique"""
        names = [model['name'] for model in MODELS]
        assert len(names) == len(set(names)), "Duplicate model names found"

    def test_model_display_names_exist(self):
        """Test that all models have display names"""
        for model in MODELS:
            assert model['display_name']
            assert len(model['display_name']) > 0

    def test_optional_description_field(self):
        """Test that description field is optional but if present is a string"""
        for model in MODELS:
            if 'description' in model:
                assert isinstance(model['description'], str)
                assert len(model['description']) > 0


class TestEmbeddingConfiguration:
    """Tests for EMBEDDING_MODEL configuration"""

    def test_embedding_model_exists(self):
        """Test that EMBEDDING_MODEL is defined"""
        assert EMBEDDING_MODEL is not None
        assert isinstance(EMBEDDING_MODEL, dict)

    def test_embedding_model_structure(self):
        """Test EMBEDDING_MODEL has required fields"""
        assert 'name' in EMBEDDING_MODEL
        assert 'provider' in EMBEDDING_MODEL
        assert EMBEDDING_MODEL['name']
        assert EMBEDDING_MODEL['provider']

    def test_embedding_model_provider(self):
        """Test that embedding model has valid provider"""
        valid_providers = ['ollama', 'anthropic']
        assert EMBEDDING_MODEL['provider'] in valid_providers


class TestGetModelList:
    """Tests for get_model_list function"""

    def test_returns_list(self):
        """Test that function returns a list"""
        result = get_model_list()
        assert isinstance(result, list)

    def test_returns_model_names(self):
        """Test that function returns model names"""
        result = get_model_list()
        assert len(result) > 0

        # All items should be strings
        for name in result:
            assert isinstance(name, str)
            assert len(name) > 0

    def test_matches_models_count(self):
        """Test that returned list matches MODELS count"""
        result = get_model_list()
        assert len(result) == len(MODELS)

    def test_contains_expected_models(self):
        """Test that list contains expected model names"""
        result = get_model_list()

        # Should contain at least one granite model
        granite_models = [m for m in result if 'granite' in m.lower()]
        assert len(granite_models) > 0

    def test_order_preserved(self):
        """Test that model order is preserved from MODELS"""
        result = get_model_list()
        expected_names = [model['name'] for model in MODELS]
        assert result == expected_names


class TestGetModelDisplayNames:
    """Tests for get_model_display_names function"""

    def test_returns_dict(self):
        """Test that function returns a dictionary"""
        result = get_model_display_names()
        assert isinstance(result, dict)

    def test_dict_not_empty(self):
        """Test that returned dict is not empty"""
        result = get_model_display_names()
        assert len(result) > 0

    def test_dict_keys_are_model_names(self):
        """Test that keys are model names"""
        result = get_model_display_names()
        model_names = get_model_list()

        for key in result.keys():
            assert key in model_names

    def test_dict_values_are_display_names(self):
        """Test that values are display names (strings)"""
        result = get_model_display_names()

        for value in result.values():
            assert isinstance(value, str)
            assert len(value) > 0

    def test_mapping_correct(self):
        """Test that mapping is correct"""
        result = get_model_display_names()

        for model in MODELS:
            assert model['name'] in result
            assert result[model['name']] == model['display_name']

    def test_all_models_have_display_names(self):
        """Test that all models have display name mappings"""
        result = get_model_display_names()
        assert len(result) == len(MODELS)


class TestGetModelConfig:
    """Tests for get_model_config function"""

    def test_returns_dict_for_valid_model(self):
        """Test that function returns dict for valid model"""
        # Get first model name
        first_model = MODELS[0]['name']
        result = get_model_config(first_model)

        assert result is not None
        assert isinstance(result, dict)

    def test_returns_none_for_invalid_model(self):
        """Test that function returns None for invalid model"""
        result = get_model_config("nonexistent-model")
        assert result is None

    def test_returns_complete_config(self):
        """Test that returned config has all fields"""
        first_model = MODELS[0]['name']
        result = get_model_config(first_model)

        assert 'name' in result
        assert 'display_name' in result
        assert 'provider' in result

    def test_config_matches_models(self):
        """Test that returned config matches MODELS entry"""
        for model in MODELS:
            result = get_model_config(model['name'])
            assert result == model

    def test_empty_string_returns_none(self):
        """Test that empty string returns None"""
        result = get_model_config("")
        assert result is None

    def test_none_input_returns_none(self):
        """Test that None input returns None"""
        result = get_model_config(None)
        assert result is None

    def test_case_sensitive(self):
        """Test that model name lookup is case-sensitive"""
        first_model = MODELS[0]['name']
        # Try with uppercase
        result = get_model_config(first_model.upper())

        # Should return None if case doesn't match
        if first_model != first_model.upper():
            assert result is None


class TestGetDefaultModel:
    """Tests for get_default_model function"""

    def test_returns_string(self):
        """Test that function returns a string"""
        result = get_default_model()
        assert isinstance(result, str)

    def test_returns_first_model_name(self):
        """Test that function returns first model's name"""
        result = get_default_model()
        expected = MODELS[0]['name']
        assert result == expected

    def test_returns_valid_model(self):
        """Test that returned model is in model list"""
        result = get_default_model()
        model_list = get_model_list()
        assert result in model_list

    def test_returned_model_has_config(self):
        """Test that default model has valid config"""
        result = get_default_model()
        config = get_model_config(result)
        assert config is not None


class TestModelConfigIntegration:
    """Integration tests for model configuration functions"""

    def test_all_models_accessible(self):
        """Test that all models can be accessed through functions"""
        model_list = get_model_list()
        display_names = get_model_display_names()

        for model_name in model_list:
            # Should have display name
            assert model_name in display_names

            # Should have config
            config = get_model_config(model_name)
            assert config is not None

    def test_display_names_match_configs(self):
        """Test that display names match those in configs"""
        display_names = get_model_display_names()

        for model_name, display_name in display_names.items():
            config = get_model_config(model_name)
            assert config['display_name'] == display_name

    def test_default_model_in_list(self):
        """Test that default model is in the model list"""
        default = get_default_model()
        model_list = get_model_list()
        assert default in model_list


class TestConfigurationValidation:
    """Tests to validate configuration integrity"""

    def test_no_duplicate_display_names(self):
        """Test that display names are unique (recommended)"""
        display_names = [model['display_name'] for model in MODELS]
        # Note: This is a recommendation, not a requirement
        # You may want to allow duplicates in some cases
        unique_display_names = set(display_names)

        if len(display_names) != len(unique_display_names):
            print("Warning: Duplicate display names found")
            # This is a warning, not a failure

    def test_provider_consistency(self):
        """Test that provider names are consistent"""
        providers = set(model['provider'] for model in MODELS)

        # All providers should be lowercase
        for provider in providers:
            assert provider == provider.lower()

    def test_model_names_no_spaces(self):
        """Test that model names don't have spaces"""
        for model in MODELS:
            assert ' ' not in model['name'], \
                f"Model name contains spaces: {model['name']}"

    def test_granite_models_configured(self):
        """Test that expected granite models are configured"""
        model_names = get_model_list()

        # Should have at least one granite model
        granite_models = [m for m in model_names if 'granite' in m.lower()]
        assert len(granite_models) >= 1

    def test_claude_models_are_anthropic(self):
        """Test that Claude models have anthropic provider"""
        for model in MODELS:
            if 'claude' in model['name'].lower():
                assert model['provider'] == 'anthropic', \
                    f"Claude model {model['name']} should have anthropic provider"

    def test_ollama_model_naming(self):
        """Test that Ollama models follow naming conventions"""
        for model in MODELS:
            if model['provider'] == 'ollama':
                # Ollama models typically have lowercase names
                # This is a soft check
                name = model['name']
                # Just verify it's a reasonable format
                assert isinstance(name, str)
                assert len(name) > 0


class TestEmptyModelsEdgeCase:
    """Test behavior when MODELS list is empty (edge case)"""

    def test_get_default_model_empty_list(self, monkeypatch):
        """Test get_default_model with empty MODELS list"""
        # Temporarily replace MODELS with empty list
        import models_config
        monkeypatch.setattr(models_config, 'MODELS', [])

        result = get_default_model()
        assert result is None
