# The default llm model used by the project
from autogen_ext.models.openai import OpenAIChatCompletionClient
default_client = OpenAIChatCompletionClient(
    model = '',
    api_key = '',
    base_url = '',
    model_info = {
        'vision': False,
        'function_calling': True,
        'json_output': True,
        'family': 'unknown',
        'structured_output': True
    }
)


# Whether to print log of the clients
PRINT_LOG = True
LOG_PATH = 'log/log.txt'