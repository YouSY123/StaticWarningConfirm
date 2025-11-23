from autogen_agentchat.agents import AssistantAgent
from config import default_client

def create_condition_generator(tools:list):
  '''
  The agent generates the conditions based on the source code and the result of the static analyzer.
  '''
  return AssistantAgent(
      name = 'Condition_generator', 
      model_client = default_client, 
      tools = tools,
      reflect_on_tool_use = True, 
      description = '',
      system_message = '''
You will be given a directory containing a cpp project and warnings on the project provided by a static analyzing tools.
Your task is to analyze and return the conditions which are used to judge the correctness of these warnings.
You should combine the warning information and the confirmation conditions in JSON format and output it. 
Please note that the JSON format must be:
```json
{
  "Files": [...],
  "Warning information":
  {
    "1": 
    {
      "File name": ,
      "Type": ,
      "Variable name": ,
      "Line number": ,
      "Data flow": ,
      "Call chain": ,
      "Confirmation conditions": {
        "1": ...,
        "2": ...,
        ...
      }
    },
    "2": {...},
    ...
  }
}
```

Then output TERMINATE
'''
  )



def create_condition_analyzer(tools:list): 
  '''
  The agent judges the correctness of the condition 
  '''
  return AssistantAgent(
  name = 'Condition_analyzer', 
      model_client = default_client, 
      tools = tools,
      reflect_on_tool_use = True,
      description = '',
      system_message = '''
You need to cooperate with others to confirm the correctness of the warnings provided by a static code analyzer. You will be given JSON format information of the program directory, warning details and a comfirmation condition. Your job is to judge whether the condition is true or false. 
You should judge the correctness of the condition and output the results (T for true, F for false) in JSON format:
```json
{"result": "T/F"}
```
Then output TERMINATE
'''
  )
