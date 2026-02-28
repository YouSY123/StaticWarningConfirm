# The default llm model used by the project
from autogen_ext.models.openai import OpenAIChatCompletionClient
import json

with open('llm_api.json', 'r') as f:
    llm_api_info = json.load(f)
    f.close()
API_KEY = llm_api_info['api_key']
BASE_URL = llm_api_info['base_url']

default_client = OpenAIChatCompletionClient(
    model = 'gpt-5-mini-2025-08-07',
    api_key = API_KEY,
    base_url = BASE_URL,
    timeout = 600,
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

CONDITION_VOTE_TIMES = 3
CONDITION_JUDGE_MAX_TURN = 1
CONDITION_CHECK_MAX_TURN = 3
CONDITION_GENERATE_MAX_TURN = 3