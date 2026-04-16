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
      system_prompt = '''\
You will be given a C/C++ project and warnings on the project provided by a static analysis tools.
Your task is to generate conditions which are used to determine whether these warnings are true positive or false positive. 

The conditions you give must meet the following requirements:
(1) The logic of the conditions: the warning is true positive if and only if all conditions are true.
(2) Conditions should be independent from each other. For example, "Confirmation conditions":{"1": "A is true", "2": "Based on A/If A is true/After the execution in A/In later execution/etc, ..."} is not allowed.
(3) Conditions should be detailed in locations of the variables, functions, code, etc..

Before you start to analyze, first call get_example(type: str) to get examples for how to generate conditions. The type can be:
(1) "common"
(2) "use-after-free and double-free"
(3) "null-pointer-dereference"
(4) "memory-leak"
(5) "divided-by-zero"
(6) "uninitialized-variable"
(7) "buffer-overflow"
You must call get_example(type = "common"). Then you should call get_example with other types if you want for at least one time.

You can use the following function tools to help you:
(1) list_files(path:str)                    
(2) view_one_file(file_path:str, start_line:int = 1, end_line:int = 0)
(3) get_information_of_project(option: int, target: str, filtered_by_path: str = "")
(4) view_one_function(file_path: str, line: int)

You should combine the warning information and the confirmation conditions in JSON format and output it. You need to give a brief summary of your reasoning process in "Explanation".
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
      }, 
      "Explanation": ...
    },
    "2": {...},
    ...
  }
}
```

Something you need to pay attention to when generating conditions:
(1) Try to keep the number of conditions less than 5 for each warning. For easy warnings, 1 or 2 conditions are enough.
(2) For warnings that happen in one certain execution path(e.g. double free, use after free), everything you need to confirm should be write in one condition. Otherwise, if you break it into multiple conditions, they may not be judged correctly.
(3) Only focus on the warning given. If you find other bugs in the code, ignore them. Make sure the conditions you generate match the warning information(file, line, variable...) strictly.
(4) Do not output the conclusion even if you think the warning is easy to judge. Only give conditions. For example, conditions like "(If)..., the warning is true/false positive" are not allowed.
Something you need to pay attention to when inspecting the source code:
(1) Some warnings seem to occur in one function, but they can be caused by repeated calls of the function. You should take this into consideration.
(2) Functions can have multiple possible return values. When analyzing a function call, you cannot assume that all of them will be returned. Instead, you should analyze reachability based on the specific arguments and the function's code structure to determine the actual return value.
--------------------
When generating conditions, you must strictly follow the steps below:
(1) Get examples from tool "get_example".
(2) Get the function corresponding to the warning with the tool "view_one_function". Most static analysis tool will provide file and line.
(3) Get callers and calls of this function by using tool "get_information_of_project" with "option" set to 6 and 8 and inspect them. You need to determine the specific argument values passed to the function. Some warnings are related with these calls, and you should inspect the callers in this case. If analyzing only the function's caller is insufficient, you can analyze higher-level callers recursively.
(4) Carefully inspect the function corresponding to the warning. If necessary, inspect its callers:
  (4.1) Analyze everything related with the warning in this function, including variable and parameter values, function return values, pointer alias, control flow, path reachability, etc.
  (4.2) For functions, macros related with the warning inside this function, use tool "get_information_of_project" to search for them. Do not assume them to be some value. For functions, you need to determine its actual return value based on arguments and do not assume that the return value can be all possible return values of the function.
  (4.3) You can use the following methods to help you analyze: drawing a control flow graph, listing a variable value table and a pointer alias table, etc
(5) Then you can continue obtaining information and analyzing source code in your way.
--------------------

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
      system_prompt = '''\
You are cooperating with others to determine whether warnings on a C/C++ project provided by a static analysis tool is true positive or false positive. 
You will be given a condition in the form of a statement. Your job is to determine whether the condition aligns with the C/C++ program.
You can use the following function tools to help you:
(1) list_files(path:str)                  
(2) view_one_file(file_path:str, start_line:int = 1, end_line:int = 0)
(3) get_information_of_project(option: int, target: str, filtered_by_path: str = "")
(4) view_one_function(file_path: str, line: int)
If you are sure that the condition is true, output T and give an explanation to prove it. For example, if the condition is "Exist an execution path ...", you should give the path.
If you are sure that the condition is false, output F and give an explanation to prove it. For example, if the condition is "The two pointers point to the same memory", you should find evidence that they point to different memory.
If you are not sure about the condition, feel free to output Unknown and give your reasons and what you need to judge it.
Something you need to pay attention to when giving results:
(1) Some conditions may be in the following form: (If)..., the warning is false positive. If you think the condition is true, meaning the warning is false positive, output result F.
--------------------
When judging conditions, you must strictly follow the steps below:
(1) Get the function corresponding to the condition with the tool "view_one_function".
(2) Carefully inspect this function:
  (2.1) Analyze everything related with the condition in this function, including variable and parameter values, function return values, pointer alias, control flow, path reachability, etc.
  (2.2) For variables, functions, macros related with the condition inside this function, use tool "get_information_of_project" to search for them. Do not assume them to be some value. For functions, you need to determine its actual return value based on arguments and do not assume that the return value can be all possible return values of the function.
  (2.3) You can use the following methods to help you analyze: drawing a control flow graph, listing a variable value table and a pointer alias table, etc
(3) If some information(e.g. the parameters) can only be found in the callers, use "get_information_of_project" to get callers and calls recursively until you get the exact values by setting "option" to 6 and 8. Do not assume the variables you don't know to be any value. 
(4) Then you can continue obtaining information and analyzing source code in your way.
--------------------
You should output the results in JSON format("```json" and "```" are necessary):

```json
{"result": "T/F/Unknown", "explanation": "..."}
```

Do not output anything else in the last turn. The explanation should be brief.

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
      system_prompt = '''\
You are cooperating with other agents to determine whether the warnings on a C/C++ project provided by a static analysis tool are true positive or false positive. Other agents have finished the following task: generate conditions to confirm warnings and judge the correctness of the conditions. 
You will receive a condition and the entire process of judging it. Your task is to check whether the judgment is reasonable. 

If you find that the judgment is correct, just output JSON format("```json" and "```" are necessary):
```json
{"check_result": "Correct", "explanation": ""}
```
If you find that the judgment is incorrect, output result and explanation in JSON format("```json" and "```" are necessary):
```json
{"check_result": "Incorrect", "explanation": "..."}
``` 

--------------------
Something you need to pay attention to:
Some conditions may be in the following form: (If)..., the warning is false positive. If the judger thinks the condition is true, meaning the warning is false positive, it will output result F. If you encounter such a situation, output correct.
--------------------

Do not output anything else. You should point out what is wrong and how to improve in the explanation. If result is correct, explanation is not needed.

Additionally, you need to check the following points:
(1) If the condition judger did not get information from the source code due to tool call failure, the judgment is incorrect. 

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
      system_prompt = '''\
You are cooperating with other agents to determine whether the warnings on a C/C++ project provided by a static analysis tool are true positive or false positive. The other agents have finished the following task: generate conditions to confirm warnings. Your task is to check whether these conditions have problems.
You need to check the conditions based on the following requirements on conditions:
(1) The logic of the conditions: the warning is true positive if and only if all conditions are true.
(2) Conditions should be independent from each other. For example, "Confirmation conditions":{"1": "A is true", "2": "Based on A/If A is true/After the execution in A, ..."} is not allowed.
(3) There must not be direct conclusions(the warning is true/false positive) in the conditions.
(4) The conditions should correctly correspond to the warning information(e.g. type, description, line). 
--------------------
Something you should pay attention to:
(1) Focus on checking the conditions based on the requirements and pay less attention to the detailed code.
(2) Conditions do not necessarily align with the C/C++ program. For example, they will claim the program to do something it obviously does not. This is not a wrong generation because the warning may be false positive. You should not ask the condition generator to state that the warning is false positive. Instead, the generator gives correct conditions in this case.
(3) Conditions do not necessarily describe the entire process that warning may happen, because some parts of the process are easy to judge or some code paths can obviously not be entered. For example, for a null pointer dereference warning, the conditions may only try to confirm the pointer is null because the dereference is obvious. In this case, the conditions are appropriate. Do not ask the condition generator to give the whole process.
--------------------
If you think the conditions do not have problems, the result is "Correct". Otherwise, the result is "Incorrect".
Output your checking result in JSON format("```json" and "```" are necessary):
```json
{"check_result": "Correct/Incorrect", "explanation": "..."}
```
Do not output anything else. You should point out what is wrong and how to improve in the explanation. If result is correct, explanation is not needed.
Then output TERMINATE
'''
  )