from config import default_model
from langchain.agents import create_agent

def create_condition_generator(tools:list):
  '''
  The agent generates the conditions based on the source code and the result of the static analyzer.
  '''
  return create_agent(
      name = 'Condition_generator', 
      model = default_model,
      tools = tools,
      system_prompt = '''
You will be given a directory containing a cpp project and warnings on the project provided by a static analyzing tools.
Your task is to analyze and return the conditions which are used to judge the correctness of these warnings. Make sure that the warning is true positive if and only if all conditions are true.
The conditions you return should be:
(1) independent from each other. That is, no condition can involve any other condition
(2) detailed in object and position so that other agents can easily understand
You can use the following function tools to help you:
(1) list_files()
    list the file structure of the whole project directory. 
    parameters: The function does not need any parameter
    call example: list_files()                     
(2) view_one_file(file_path:str, start_line:int = 1, end_line:int = 0)
    view a file with address file_path from start_line to end_line.
    parameters: file_path, start_line(default: 1), end_line(default: the last line)
    call example: view_one_file(file_path='main.c', start_line=1, end_line=20)
(3) search_in_directory(pattern:str, dir:str)
    search a string pattern in a directory
    parameters: pattern, dir
    call example: search_in_directory(pattern='malloc', dir='src/')
Before you start to analyze, first call get_example(type: str) to get examples for how to generate conditions. The type can be:
(1) "common"
(2) "use-after-free"
(3) "double-free"
You must call get_example(type = "common"). Then you should call get_example with other types if you want for at least one time.

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
Do not output anything else in the last turn.

Attention:
(1) Do not generate too many conditions. Try to keep the number of conditions less than 5 for each warning. For easy warnings, 1 or 2 conditions are enough.
(2) For warnings that happen in one certain execution path(e.g. double free, use after free), everything you need to confirm should be write in one condition. Otherwise, if you break it into multiple conditions, they may not be judged correctly.
(3) Some warnings seem to occur in one function, but they can be caused by repeated calls of the function. You should take this into consideration when generating conditions.
(4) Conditions cannot depend on each other. For example: "Confirmation conditions":{"1": "A is true", "2": "Based on A/If A is true, ..."} is not allowed.
(5) Only focus on the warning given. If you find other bugs in the code, ignore them. Make sure the conditions you generate match the warning information(file, line, variable...) strictly.

Then output TERMINATE
'''
  )



def create_condition_analyzer(tools:list): 
  '''
  The agent judges the correctness of the condition 
  '''
  return create_agent(
      name = 'Condition_analyzer', 
      model = default_model, 
      tools = tools,
      system_prompt = '''
You need to cooperate with others to confirm the correctness of the warnings provided by a static code analyzer. You will be given JSON format information of the program directory, warning details and a comfirmation condition. Your job is to judge whether the condition is true or false. 
You can use the following function tools to help you:
(1) list_files()
    list the file structure of the whole project directory. 
    parameters: The function does not need any parameter
    call example: list_files()                     
(2) view_one_file(file_path:str, start_line:int = 1, end_line:int = 0)
    view a file with address file_path from start_line to end_line.
    parameters: file_path, start_line(default: 1), end_line(default: the last line)
    call example: view_one_file(file_path='main.c', start_line=1, end_line=20)
(3) search_in_directory(pattern:str, dir:str)
    search a string pattern in a directory
    parameters: pattern, dir
    call example: search_in_directory(pattern='malloc', dir='src/')
You should judge the correctness of the condition and output the results in JSON format("```json" and "```" are necessary):

```json
{"result": "T/F/Unknown", "explanation": "..."}
```

Do not output anything else in the last turn. The explanation should be brief.

If you are sure that the condition is true, output T and give an explanation to prove it. For example, if the condition is "Exist an execution path ...", you should give the path.
If you are sure that the condition is false, output F and give an explanation to prove it. For example, if the condition is "The two pointers point to the same memory", you should find evidence that they point to different memory.
If you are not sure about the condition, feel free to output Unknown and give your reasons and what you need to judge it.

Then output TERMINATE
'''
  )


def create_condition_judge_checker_agent():
  '''
  The agent checks whether the condition judgment is correct
  '''
  return create_agent(
      name = 'Condition_judge_checker',
      model = default_model, 
      system_prompt = '''
You are cooperating with others to confirm the correctness of the warnings provided by a static code analyzer. The previous agent has finished the following task: generate conditions to confirm warnings and judge the correctness of the conditions. Your task is to check whether the judgment of the conditions is correct.
You will be given JSON format information of the program directory, warning details, a confirmation condition and the judgment of the condition. Your job is to check whether the judgment is correct. 
The judgment contains result and the whole process. The key is to check whether the process is reasonable and can support the result.

If you find that the judgment is correct, just output JSON format("```json" and "```" are necessary):
```json
{"check_result": "Correct", "explanation": ""}
```
If you find that the judgment is incorrect, output result and explanation in JSON format("```json" and "```" are necessary):
```json
{"check_result": "Incorrect", "explanation": "..."}
``` 

Do not output anything else. The explanation should be brief. If result is correct, explanation is not needed.

Additionally, you need to check the following points:
(1) The judger should get enough imformation from tools. If some key information is missing due to tool call failure, the result is incorrect.

Then output TERMINATE
'''
  )


def create_condition_checker_agent():
  '''
  The agent checks whether the conditions generated are appropriate
  '''
  return create_agent(
      name = 'Condition_checker',
      model = default_model, 
      system_prompt = '''
You are cooperating with others to confirm the correctness of the warnings provided by a static code analyzer. The previous agent has finished the following task: generate conditions to confirm warnings. Your task is to check whether the generated conditions are appropriate.
You need to check the conditions based on the following points:
(1) All conditions should be independent from each other. That is, no condition can involve any other condition.
(2) The conditions correctly correspond to the warning information(e.g., variable name, line number, type).
(3) The condition generator should get enough imformation from tools. If some key information is missing due to tool call failure, the result is incorrect.
Output your checking result in JSON format("```json" and "```" are necessary):
```json
{"check_result": "Correct/Incorrect", "explanation": "..."}
```
Do not output anything else. The explanation should be brief. If result is correct, explanation is not needed.
Then output TERMINATE
'''
  )