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
Your task is to analyze and return the conditions which are used to judge the correctness of these warnings. Make sure that the warning is true positive if and only if all conditions are true.
The conditions you return should be:
(1) independent from each other. That is, no condition can involve any other condition
(2) detailed in object and position so that other agents can easily understand
You can use the following function tools to help you(When passing directory address, use absolute path):
(1) list_files
    list the file structure of the whole project directory. 
    parameters: The function does not need any parameter
    call example: list_files()                     
(2) view_one_file
    view a file with address file_path from start_line to end_line.
    parameters: file_path, start_line(default: 1), end_line(default: the last line)
    call example: view_one_file(file_path='main.c', start_line=1, end_line=20)
(3) grep_in_directory
    search a string pattern in a directory
    parameters: pattern, dir
    call example: grep_in_directory(pattern='malloc', dir='src/')
Before you start to analyze, first call examples_for_use_after_free and examples_for_double_free to learning condition generation.
You should combine the warning information and the confirmation conditions in JSON format and output it. 
Please note that the JSON format must be("```json" and "```" are necessary in your answer):
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
You can use the following function tools to help you:
(1) list_files: list the file structure of the whole directory                       
(2) view_one_file: pass the address of a file(based on the project directory), start line(default: 1), end line(default: the last line) and get the file content
(3) grep_in_directory: use it like shell command 'grep'. Pass a regex pattern and the directory and get the position of the string
You should judge the correctness of the condition and output the results (T for true, F for false) in JSON format("```json" and "```" are necessary):
```json
{"result": "T/F"}
```
Then output TERMINATE
'''
  )
