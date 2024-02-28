import pytest

from map_reduce_cli.token_math import get_remaining_token_limit, get_token_size, get_chunk_limit_for_mapper


def test_get_remaining_token_limit():
    query = "What is the capital of France?"
    summary = "The capital of France is Paris."
    max_token_limit = 500
    remaining = get_remaining_token_limit(query, summary, max_token_limit)
    assert remaining == 500 - 14


def test_get_token_size():
    short_text = "Hello"
    assert get_token_size(short_text) == 1

    long_text = "This is a much longer string with many more tokens"
    assert get_token_size(long_text) > 8


@pytest.mark.parametrize("doc_len,expected_chunks", [
    (400, 1),
    (600, 2)
])
def test_get_chunk_limit_for_mapper(doc_len, expected_chunks):
    query_len = 10
    max_token_limit = 500

    chunk_size, num_chunks = get_chunk_limit_for_mapper(doc_len, query_len, max_token_limit)

    assert num_chunks == expected_chunks
    assert chunk_size < max_token_limit
