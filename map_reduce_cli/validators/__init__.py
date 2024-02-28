import os.path
import yaml
import logging

logger = logging.getLogger('LargeDocumentProcessor')
# Configure root logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s')



class Validator:
    def __init__(self, data):
        self.data = data
        self.validate()

    def validate(self):
        pass


class PromptConfig(Validator):
    MANDATORY_KEYS = ['prompt_template', 'prompt_template_var', 'map_reduce_method']
    OPTIONAL_KEYS = ['chunk_size', 'reducer_template', 'reduce_template_var', 'step_delay_in_seconds',
                     'map_response_regex_filter']

    def __init__(self, config_loc: str):
        if not os.path.exists(config_loc):
            raise FileNotFoundError(f'Path {config_loc} not found. Please confirm the parameter.')
        with open(config_loc, 'r') as re:
            data = yaml.safe_load(re)
        super().__init__(data)
        self.max_token_limit = 2096
        self.map_response_regex_filter = None
        self.step_delay_in_seconds = 5
        for key, value in data.items():
            setattr(self, key, value)

    def validate(self):
        for m in self.MANDATORY_KEYS:
            if m not in self.data.keys():
                raise AssertionError(
                    f'Required keys are missing from config file. Required list is {self.MANDATORY_KEYS}')
        exception_list = {}
        for k, v in self.data.items():
            match k:
                case 'prompt_template':
                    if type(v) != str:
                        exception_list[k] = f'Found type {type(v)}. Expected str'
                    break
                case 'max_token_limit':
                    if type(v) == int:
                        self.max_token_limit = v
                    break
                case 'prompt_template_var':
                    if type(v) != str:
                        exception_list[k] = f'Found type {type(v)}. Expected str'
                    break
                case 'reducer_template_var':
                    if type(v) != str:
                        exception_list[k] = f'Found type {type(v)}. Expected str'
                    break
                case 'map_reduce_method':
                    allowed_values = ['parallel', 'refine']
                    if type(v) != str:
                        exception_list[k] = f'Found type {type(v)}. Expected str'
                    elif v not in allowed_values:
                        exception_list[
                            k] = f'Unexpected value {v}. Expected values are {type(v)}. Expected values are {allowed_values}'
                    break
                case 'chunk_size':
                    if type(v) != int:
                        exception_list[k] = f'Found type {type(v)}. Expected int'
                    break
                case 'reducer_template':
                    if type(v) != str:
                        exception_list[k] = f'Found type {type(v)}. Expected str'
                    break
                case 'step_delay_in_seconds':
                    if type(v) != int or v < 0:
                        exception_list[k] = f'Found type {type(v)}. Expected str'
                    break
                case 'map_response_regex_filter':
                    if type(v) != str:
                        exception_list[k] = f'Found type {type(v)}. Expected str'
                    break
        logger.info('Prompt config set up complete...')


class Secrets(Validator):
    MANDATORY_KEYS = ['model_env_vars']

    def __init__(self, secrets_loc: str):
        if not os.path.exists(secrets_loc) or not os.path.isfile(secrets_loc):
            raise FileNotFoundError(f'Path {secrets_loc} not found or is not a file. Please confirm the parameter.')
        with open(secrets_loc, 'r') as re:
            data = yaml.safe_load(re)
        super().__init__(data)
        for key, value in data['model_env_vars'].items():
            setattr(self, key, value)

    def validate(self):
        if self.data['model_env_vars'] is None:
            raise AssertionError(
                'No environment variable configurations were found. Please address the Prompt Config file')
        else:
            for m in self.MANDATORY_KEYS:
                if m not in self.data.keys():
                    raise AssertionError(
                        f'Required keys are missing from config file. Required list is {self.MANDATORY_KEYS}')
            exception_list = {}
            for k, v in self.data['model_env_vars'].items():
                os.environ[k] = v
            logger.info('Environment setup for model interaction complete...')


class DataFolder(Validator):

    def __init__(self, data_loc: str):
        if not os.path.exists(data_loc):
            raise FileNotFoundError(f'Path {data_loc} not found. Please confirm the parameter.')
        self.is_folder = not os.path.isfile(data_loc)
        super().__init__(data_loc)

    def validate(self):
        pass
