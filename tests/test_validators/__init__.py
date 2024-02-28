import os
import pytest
from map_reduce_cli.validators import Validator, PromptConfig, Secrets


def test_validator_validate():
    # Test base Validator class
    data = {'key1': 'value1'}
    validator = Validator(data)
    validator.validate()
    assert validator.data == data


def test_promptconfig():
    # Test PromptConfig class

    # Test invalid config path
    with pytest.raises(FileNotFoundError):
        PromptConfig('invalidpath')

    # Test missing mandatory keys
    data = ''
    with pytest.raises(AssertionError):
        PromptConfig(data)

    # Test invalid data types
    data = {'prompt_template': 123,
            'template_vars': True,
            'map_reduce_method': None}
    with pytest.raises(AssertionError):
        PromptConfig(data)

    # Test invalid map_reduce_method value
    data = {'prompt_template': 'template',
            'template_vars': 'vars',
            'map_reduce_method': 'invalid'}
    with pytest.raises(AssertionError):
        PromptConfig(data)

    # Test valid case
    data = {'prompt_template': 'template',
            'template_vars': 'vars',
            'map_reduce_method': 'parallel'}
    prompt_config = PromptConfig(data)
    assert prompt_config.data == data


def test_secrets():
    # Test Secrets class

    # Test missing mandatory keys
    data = {}
    with pytest.raises(AssertionError):
        Secrets(data)

    # Test invalid data type
    data = {'model_env_vars': 'env'}
    with pytest.raises(AssertionError):
        Secrets(data)

    # Test valid case
    data = {'model_env_vars': {'KEY1': 'val1', 'KEY2': 'val2'}}
    secrets = Secrets(data)
    assert secrets.data == data
