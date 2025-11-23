from agents import create_condition_analyzer, create_condition_generator
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
import asyncio
from autogen_core.tools import FunctionTool
from tools import AgentTools
import json
from copy import deepcopy


from config import PRINT_LOG, LOG_PATH
def print_client_log(title:str, content:str):
    if not PRINT_LOG:
        return
    with open(LOG_PATH, 'a') as f:
        f.write(f'----------{title}----------\n')
        f.write(f'{content}\n')
        f.write(f'----------End {title}----------\n\n\n')
    f.close()


class StaticAnalysisWarningsConfirmation:

    def __init__(self, root_dir, make_cmd, static_analysis_result, database_path, codeql_result_dir):

        self.root_dir = root_dir
        self.make_cmd = make_cmd
        self.sar = static_analysis_result
        self.agent_tools = AgentTools(src_path=root_dir, database_path=database_path, build_command=make_cmd, result_dir=codeql_result_dir)
        self.cmd_tool = FunctionTool(func=self.agent_tools.run_cmd, name='cmd_tool', description='Use cmd with this tool.')
        self.condition_generator = create_condition_generator([self.cmd_tool])


    async def generate_conditions(self, input_info:str):
        
        team = RoundRobinGroupChat(
            participants = [self.condition_generator],
            max_turns = 100,
            termination_condition=TextMentionTermination("TERMINATE")
        )

        result = await team.run(task = input_info)

        if PRINT_LOG:
            dialogue = ''
            for i in range(len(result.messages)):
                dialogue += str(result.messages[i].content)
                dialogue += '\n\n'
            print_client_log('Condition Generator', dialogue)

        return result.messages[-1].content
    

    def extract_json(self, string_info:str):

        if '```json' in string_info:
            parts = string_info.split('```json')
            string_info = parts[1]
        if '```' in string_info:
            parts = string_info.split('```')
            string_info = parts[0]

        try:
            json_info = json.loads(string_info)
            return json_info
        except Exception as e:
            print("Wrong format of JSON")
            return {}
    

    async def judge_conditions(self, json_info, tools:list):

        condition_analyzer = create_condition_analyzer(tools)

        team = RoundRobinGroupChat(
            participants = [condition_analyzer],
            max_turns = 100,
            termination_condition=TextMentionTermination("TERMINATE")
        )

        result = await team.run(task = json_info)

        if PRINT_LOG:
            dialogue = ''
            for i in range(len(result.messages)):
                dialogue += str(result.messages[i].content)
                dialogue += '\n\n'
            print_client_log('Condition Inspector', dialogue)

        return self.extract_json(result.messages[-1].content)

    

    async def start(self):

        if PRINT_LOG:
            with open(LOG_PATH, 'w') as f:
                f.write('')
            f.close()
        print_client_log('Input', f'Root directory: {self.root_dir}\nMake command: {self.make_cmd}\nAnalysis result:\n{self.sar}\n')

        # get prompt for the first agent to generate the conditions
        generate_prompt = 'The directory of the project: ' + self.root_dir + '\nThe result of the static analyzer:\n' + self.sar
        
        # generate and extract the conditions
        conditions = await self.generate_conditions(generate_prompt)
        conditions_json = self.extract_json(conditions)

        # extract the conditions and get prompts for each judging agent
        judger_prompt = []
        if 'Warning information' in conditions_json:
            for w in conditions_json['Warning information']:
                warning = conditions_json['Warning information'][w]
                if "Confirmation conditions" in warning:
                    for c in warning["Confirmation conditions"]:
                        confirmation = warning["Confirmation conditions"][c]
                        new_prompt_json = deepcopy(warning)
                        new_prompt_json["Confirmation conditions"] = confirmation
                        judger_prompt.append(json.dumps(new_prompt_json))
                else:
                    print('Wrong format of conditions')
        else:
            print('Wrong format of conditions')
            return

        # send prompts to agents by asyncio
        judge_tasks = [self.judge_conditions(json_info, [self.cmd_tool]) for json_info in judger_prompt]
        results = await asyncio.gather(*judge_tasks)
        
        print_client_log('Final Result', str(results))



if __name__ == '__main__':
    dir = '/home/shuyang/Project/SAConfirm/test'
    command = 'g++ test.cpp -o test'
    result = '''
    Checking test.cpp ...
    test.cpp:7:5: error: Dereferencing 'test' after it is deallocated / released [deallocuse]
        test[0] = 1;
        ^
    test.cpp:6:15: error: Memory is allocated but not initialized: test [uninitdata]
        delete [] test;
                ^
    '''
    db_path = 'test/database_test'
    codeql_result_dir = 'CodeQL/'
    sawc = StaticAnalysisWarningsConfirmation(dir, command, result, db_path, codeql_result_dir)
    asyncio.run(sawc.start())