import tiktoken


def get_remaining_token_limit(query: str, summary: str, max_token_limit: int) -> int:
    query_len = get_token_size(query)
    summary_len = get_token_size(summary)
    return max_token_limit - (query_len + summary_len)


def get_token_size(text: str) -> int:
    tokenizer = tiktoken.get_encoding('cl100k_base')
    return len(tokenizer.encode(text))


def get_chunk_limit_for_mapper(document_length: int, query_len: int, max_token_limit: int) -> (int, int):
    if document_length + query_len < max_token_limit:
        return (document_length + query_len), 1
    else:
        chunking_pool = max_token_limit - query_len
        num_chunks = int(document_length / chunking_pool) + 1
        chunk_size = int(document_length / num_chunks) + query_len
        return chunk_size, num_chunks
