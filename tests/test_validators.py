import json
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
    with pytest.raises(FileNotFoundError):
        PromptConfig(data)

    # Test invalid data types
    data = '/a/b/c/'
    with pytest.raises(FileNotFoundError):
        PromptConfig(data)


def test_secrets():
    # Test Secrets class

    # Test missing mandatory keys
    data = ''
    with pytest.raises(FileNotFoundError):
        Secrets(data)
