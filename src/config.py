# The default llm model used by the project
import json
from langchain_openai import ChatOpenAI

with open('llm_api.json', 'r') as f:
    llm_api_info = json.load(f)
    f.close()
API_KEY = llm_api_info['api_key']
BASE_URL = llm_api_info['base_url']
MODEL = llm_api_info['model']


default_model = ChatOpenAI(
    model=MODEL, 
    api_key=API_KEY, 
    base_url=BASE_URL,
    timeout=600, 
    reasoning_effort="medium", 
    temperature=0.2
)

# Whether to print log of the clients
PRINT_LOG = True

CONDITION_VOTE_TIMES = 5
CONDITION_JUDGE_MAX_TURN = 2
CONDITION_CHECK_MAX_TURN = 3
CONDITION_GENERATE_MAX_TURN = 5
CONDITION_GENERATE_RETRY_TIMES = 3