from agents import create_condition_analyzer, create_condition_generator
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
import asyncio
from autogen_core.tools import FunctionTool
from tools import AgentTools
import json
from copy import deepcopy


from config import PRINT_LOG
def print_client_log(title:str, content:str, log_path:str):
    if not PRINT_LOG:
        return
    with open(log_path, 'a') as f:
        f.write(f'----------{title}----------\n')
        f.write(f'{content}\n')
        f.write(f'----------End {title}----------\n\n\n')
    f.close()


class StaticAnalysisWarningsConfirmation:

    def __init__(self, root_dir, make_cmd, static_analysis_result, database_path, codeql_result_dir, result_path):

        self.root_dir = root_dir
        self.make_cmd = make_cmd
        self.sar = static_analysis_result
        self.agent_tools = AgentTools(src_path=root_dir, database_path=database_path, build_command=make_cmd, tempfile_dir=codeql_result_dir)
        self.result_path = result_path

    async def generate_conditions(self, input_info:str):
        # create tools for the agent
        list_files = FunctionTool(func=self.agent_tools.list_files, name='list_files', description='')
        view_one_file = FunctionTool(func=self.agent_tools.view_one_file, name='view_one_file', description='')
        grep_in_directory = FunctionTool(func=self.agent_tools.grep_in_directory, name='grep_in_directory', description='')

        from fewshot import get_use_after_free_example, get_double_free_example
        examples_for_uaf = FunctionTool(func=get_use_after_free_example, name='examples_for_use_after_free', description='Get examples for use-after-free conditions.')
        examples_for_df = FunctionTool(func=get_double_free_example, name='examples_for_double_free', description='Get examples for double-free conditions.')

        # create agent
        condition_generator = create_condition_generator([list_files, 
                                                          view_one_file, 
                                                          grep_in_directory, 
                                                          examples_for_uaf, 
                                                          examples_for_df])
        team = RoundRobinGroupChat(
            participants = [condition_generator],
            max_turns = 100,
            termination_condition=TextMentionTermination("TERMINATE")
        )

        result = await team.run(task = input_info)

        if PRINT_LOG:
            dialogue = ''
            for i in range(len(result.messages)):
                dialogue += str(result.messages[i].content)
                dialogue += '\n\n'
            print_client_log('Condition Generator', dialogue, self.result_path)

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
    

    async def judge_conditions(self, json_info, tools:list, index = 0):

        # run condition judging agents for several times
        from config import CONDITION_JUDGE_TIMES, CONDITION_JUDGE_MAX_TURN

        judge_cnt = 0



        async def judge_one_time():
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
                print_client_log(f'Condition Inspector {index}', dialogue, self.result_path)
            result_json = self.extract_json(result.messages[-1].content)
            return result_json
        

        while judge_cnt < CONDITION_JUDGE_MAX_TURN:
            judge_tasks = [judge_one_time() for i in range(CONDITION_JUDGE_TIMES)]
            judge_result_list = await asyncio.gather(*judge_tasks)
            true_cnt = 0
            false_cnt = 0
            for r in judge_result_list:
                if 'result' in r:
                    r_str = r['result']
                    if r_str == 'T' or r_str == 't': true_cnt += 1
                    elif r_str == 'F' or r_str == 'f': false_cnt += 1
            if true_cnt > false_cnt: return {f'result for condition {index}': 'T', 'T Num': true_cnt, 'F Num': false_cnt}
            elif false_cnt > true_cnt: return {f'result for condition {index}': 'F', 'T Num': true_cnt, 'F Num': false_cnt}
            else: judge_cnt += 1

        return {f'result for condition {index}': 'N'}

    

    async def start(self):

        if PRINT_LOG:
            with open(self.result_path, 'w') as f:
                f.write('')
            f.close()
        print_client_log('Input', f'Root directory: {self.root_dir}\nMake command: {self.make_cmd}\nAnalysis result:\n{self.sar}\n', self.result_path)

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
                        new_prompt_json['Project path'] = self.root_dir
                        judger_prompt.append(json.dumps(new_prompt_json))
                else:
                    print('Wrong format of conditions')
                    return
        else:
            print('Wrong format of conditions')
            return

        # send prompts to agents by asyncio
         # create tools for the agent
        list_files = FunctionTool(func=self.agent_tools.list_files, name='list_files', description='')
        view_one_file = FunctionTool(func=self.agent_tools.view_one_file, name='view_one_file', description='')
        grep_in_directory = FunctionTool(func=self.agent_tools.grep_in_directory, name='grep_in_directory', description='')
        # create agent
        judge_tasks = [self.judge_conditions(json_info, [list_files, view_one_file, grep_in_directory], idx+1) for idx, json_info in enumerate(judger_prompt)]
        llm_results = await asyncio.gather(*judge_tasks)
        result = []
        result_ptr = 0
        for w in conditions_json['Warning information']:
            warning = conditions_json['Warning information'][w]
            warning_result = {}
            for index_condition, c in enumerate(warning["Confirmation conditions"]):
                warning_result[str(index_condition+1)] = llm_results[result_ptr]
                result_ptr += 1
            result.append(warning_result)

        print_client_log('Results for conditions', f'''\
conditions:
{str(conditions_json)}
results:       
{str(result)}
        ''', self.result_path)

        final_results = []
        for c in result:
            condition_result = 'True positive'
            for key, r in c.items():
                if (list(r.values()))[0] == 'F':
                    condition_result = 'False positive'
                    break
            final_results.append(condition_result)
        print_client_log('Final results', str(condition_result), self.result_path)

        return final_results
            

if __name__ == '__main__':
    # dir: project root directory 最好是本地绝对路径
    # command: project build command
    # result: result of the static analysis
    # db_path: the path to save the database of CodeQL   目前还没有使用CodeQL的工具函数
    # codeql_result_dir: the path to save the result files of CodeQL

    static_analysis_result = '''\
{
    "bug_type": "Null Pointer Dereference",
    "line": 24,
    "column": 3,
    "procedure": "",
    "file": "npd.c",
    "qualifier": {
        "Cppcheck": "Possible null pointer dereference: buf"
    },
    "Trace": [
        {"filename": "npd.c", "line_number": 24, "column_number": 3, "description": ""},
        {"filename": "npd.c", "line_number": 21, "column_number": 21, "description": ""},
        {"filename": "npd.c", "line_number": 46, "column_number": 18, "description": ""}
    ]
}
'''


    swac = StaticAnalysisWarningsConfirmation(
        root_dir='/home/shuyang/Project/LLM4SA/test/npd',
        make_cmd='',
        static_analysis_result=static_analysis_result,
        database_path='',
        codeql_result_dir='',
        result_path='/home/shuyang/Project/llm4sa-tests/test/test.txt'
    )

    asyncio.run(swac.start())