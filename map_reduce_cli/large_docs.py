# Copyright [2024] Krishnan Narayan
#
# Licensed under CC BY-SA 4.0 (see LICENSE file)
import argparse
import json
import os
import re
import subprocess
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureOpenAI
from validators import Secrets, PromptConfig, DataFolder
from textractors import text_extractor
from token_math import get_token_size
import logging

logger = logging.getLogger('LargeDocumentProcessor')
# Configure root logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s')


class LongDocProcessor:
    DEFAULT_READ_CHUNK_SIZE = 5000
    DEFAULT_PADDING = 100

    def __init__(self, args):
        self.secrets_file = args.secrets
        self.config_file = args.config
        self.data_folder = args.data
        self.secrets = Secrets(self.secrets_file)
        self.prompt_config = PromptConfig(self.config_file)
        self.data_handler = DataFolder(self.data_folder)
        self.job_id = uuid.uuid4()
        self.output_queue = Queue()
        self.model = AzureOpenAI(azure_deployment='pcs-arch-kb', streaming=True)

    @staticmethod
    def _token_size_for_file(f):

        char_size = int(subprocess.check_output(['wc', '-m', f]).split()[0])
        return round(char_size ** 0.5)

    @staticmethod
    def _token_size_for_str(s):
        return get_token_size(s)

    def process(self, debug=False):
        os.makedirs(f'/tmp/llm-map-reduce/job-{self.job_id}', exist_ok=True)
        # Start job prep by first creating chunks of data
        text_doc_loc = text_extractor(self.data_folder)
        if os.path.isdir(text_doc_loc):
            # if folder - get all the child documents and perform map() operation
            # on each child document separately
            for file in os.listdir(text_doc_loc):
                # extract text from each child document
                file_path = os.path.join(text_doc_loc, file)
                self.llm_map(file=file_path)
        else:
            # document is single and do map operation on text_doc_loc itself.
            # Then submit chunks to token math library
            self.llm_map(file=text_doc_loc)
        if not debug:
            os.rmdir(f'/tmp/llm-map-reduce/job-{self.job_id}')

    def llm_map(self, file=None):
        # raise exception if file location or file is not provided
        if not file or type(file) != str or not os.path.isfile(file):
            raise ValueError("File location or file is not provided")
        # get size of file
        q_tokens = self._token_size_for_str(self.prompt_config.prompt_template)
        intermediate_result_path = f'/tmp/llm-map-reduce/job-{self.job_id}/'
        chunk_id = 0
        if self.prompt_config.map_reduce_method == 'parallel':
            with ThreadPoolExecutor(max_workers=4) as executor:
                c_token_len = 0
                p_chunk = ''
                for chunk in self._read_in_chunks(file, self.DEFAULT_READ_CHUNK_SIZE):
                    c_token_len += get_token_size(chunk)
                    p_chunk += chunk
                    # compute remaining space
                    backfill_token_size = self.prompt_config.max_token_limit - c_token_len - q_tokens - 100
                    if c_token_len >= backfill_token_size:
                        executor.submit(self._mapper, p_chunk, chunk_id, intermediate_result_path)
                        chunk_id += 1
                        c_token_len = 0
                        p_chunk = ''
                    # sleep for max 2 mins or configured interval
                    delay = self.prompt_config.step_delay_in_seconds
                    if delay and type(delay) == int:
                        delay = delay if delay < 120 else 120
                        time.sleep(delay)
                if p_chunk:
                    executor.submit(self._mapper, p_chunk, chunk_id, intermediate_result_path)

            executor.shutdown(wait=True)
            # reduce function here once all results are collected
            self._reduce(intermediate_result_path)
        else:
            chunk_id = 0
            for chunk in self._read_in_chunks(file, self.DEFAULT_READ_CHUNK_SIZE):
                self._mapper(chunk, chunk_id=chunk_id, intermediate_result_path=intermediate_result_path)
                chunk_id += 1

    @staticmethod
    def _read_in_chunks(file, chunk_size):
        """Generator to read file in chunks"""
        with open(file, 'r') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    def _mapper(self, document: str, chunk_id: int, intermediate_result_path: str = None):
        logger.info(f"Processing chunk {chunk_id} with size {len(document)}")
        result_loc = intermediate_result_path + str(chunk_id)
        chain = PromptTemplate.from_template(self.prompt_config.prompt_template) | self.model | StrOutputParser()
        result = chain.invoke({self.prompt_config.prompt_template_var: document})
        result = result.replace('Answer:', '')
        result = self.filtered(result, self.prompt_config.map_response_regex_filter)
        if result and result != '':
            with open(result_loc, 'w+') as w:
                w.write(result)
        logger.info(f'Chunk {chunk_id} processing complete')

    def _reduce(self, intermediate_result_path):
        logger.info(f'Starting reducer for job {self.job_id}')
        # Compose all intermediate results from files to in memory list object
        results = []
        # Iterate through all chunk result files
        for chunk_id in os.listdir(intermediate_result_path):
            # Read each chunk result file
            with open(os.path.join(intermediate_result_path, chunk_id)) as f:
                results.append(f.read())
        chain = PromptTemplate.from_template(self.prompt_config.reducer_template) | self.model | StrOutputParser()
        try:
            reduced_answer = chain.invoke({self.prompt_config.reducer_template_var: results})
        except Exception as e:
            logger.error(f'Reducer failed with error: {e}')
            reduced_answer = str(e)
        with open(intermediate_result_path + 'reduced_answer', 'w+') as w:
            w.write(json.dumps({'intermediate_answers': results,
                                'final_answer': reduced_answer}))
        logger.info(f'Reducer complete for job {self.job_id}')

    @staticmethod
    def filtered(result, regex=None):
        if not regex:
            return result
        return result if re.match(regex, result) else ''


if __name__ == '__main__':
    args = argparse.ArgumentParser(
        usage='python3 large_docs.py --data <path to data folder> --config <path to config file> --secrets <path to secrets file>',
        description='CLI to enable large document processing with LLMs')
    args.add_argument('--data', required=True, type=str,
                      help='Path to the folder that needs to be processed')
    args.add_argument('--config', required=True, type=str,
                      help='Path to prompt_config.yml document that will guide how the file will be analyzed')
    args.add_argument('--secrets', required=True, type=str,
                      help='Path to secrets.yml document that will contain LLM model specs and credentials')

    args = args.parse_args()
    processor = LongDocProcessor(args)
    processor.process()
    logger.info(f'Job {processor.job_id} is complete...')
