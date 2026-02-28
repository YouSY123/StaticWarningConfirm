from agents import create_condition_analyzer, create_condition_generator, create_condition_judge_checker_agent
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
            string_info = parts[-1]
        if '```' in string_info:
            parts = string_info.split('```')
            string_info = parts[0]
        while string_info[-1] != "}" : 
            string_info = string_info[:-1]

        try:
            json_info = json.loads(string_info)
            return json_info
        except Exception as e:
            print("Wrong format of JSON")
            return "Error"
    

    async def judge_conditions(self, json_info, tools:list, index = 0):

        # run condition judging agents for several times
        from config import CONDITION_VOTE_TIMES, CONDITION_JUDGE_MAX_TURN

        judge_cnt = 0

        async def judge_one_time():

            from config import CONDITION_CHECK_MAX_TURN

            log_info = ''

            judge_pass = False

            for judge_try in range(CONDITION_CHECK_MAX_TURN):

                condition_analyzer = create_condition_analyzer(tools)
                team = RoundRobinGroupChat(
                    participants = [condition_analyzer],
                    max_turns = 100,
                    termination_condition=TextMentionTermination("TERMINATE")
                )
                result = await team.run(task = json_info)

                dialogue = ''
                for i in range(len(result.messages)):
                    dialogue += str(result.messages[i].content)
                    dialogue += '\n\n'

                log_info += f"Judge try {judge_try+1}:\n" + dialogue + "\n\n" 

                result_json = self.extract_json(result.messages[-1].content)
                if result_json == 'Error': 
                    log_info += f"Judge try {judge_try+1} result: JSON format error.\n\n"
                    continue


                checker_prompt = f"Condition confirmation information:\n{json_info}\n\nCondition judgment to be checked:\n{json.dumps(result_json)}"
                condition_judge_checker = create_condition_judge_checker_agent(tools)
                checker_team = RoundRobinGroupChat(
                    participants = [condition_judge_checker],
                    max_turns = 100,
                    termination_condition=TextMentionTermination("TERMINATE")
                )
                checker_result = await checker_team.run(task = json.dumps(checker_prompt))

                checker_dialogue = ''
                for i in range(len(checker_result.messages)):
                    checker_dialogue += str(checker_result.messages[i].content)
                    checker_dialogue += '\n\n'
                log_info += f"Checker for try {judge_try+1}:\n" + checker_dialogue + "\n\n"

                # print(checker_result.messages[-1].content)

                checker_result_json = self.extract_json(checker_result.messages[-1].content)
                if "check_result" in checker_result_json:
                    if checker_result_json['check_result'] == 'Correct':
                        judge_pass = True
                        log_info += f"Judge try {judge_try+1} result: Correct.\n\n"
                        break
                    else:
                        log_info += f"Judge try {judge_try+1} result: Incorrect.\n\n"

            print_client_log(f'Condition Inspector {index}', log_info, self.result_path)

            if judge_pass:
                return result_json
            else:
                return {"result": "Unknown", "explanation": "Not pass check"}

        while judge_cnt < CONDITION_JUDGE_MAX_TURN:
            judge_tasks = [judge_one_time() for i in range(CONDITION_VOTE_TIMES)]
            judge_result_list = await asyncio.gather(*judge_tasks)
            true_cnt = 0
            false_cnt = 0
            unknown_cnt = 0
            true_reasons = []
            false_reasons = []
            unknown_reasons = []
            for r in judge_result_list:
                if 'result' in r:
                    r_str = r['result']
                    if r_str == 'T' or r_str == 't': 
                        true_cnt += 1
                        true_reasons.append(r.get('explanation', ''))
                    elif r_str == 'F' or r_str == 'f': 
                        false_cnt += 1
                        false_reasons.append(r.get('explanation', ''))
                    elif r_str == 'Unknown' or r_str == 'unknown': 
                        unknown_cnt += 1
                        unknown_reasons.append(r.get('explanation', ''))
            if true_cnt > max(false_cnt, unknown_cnt):
                return {
                    f"result for condition {index}": 'T',
                    'T Num': true_cnt,
                    'F Num': false_cnt,
                    "Unknown Num": unknown_cnt,
                    "T reasons": true_reasons,
                    "F reasons": false_reasons,
                    "Unknown reasons": unknown_reasons
                }
            elif false_cnt > max(true_cnt, unknown_cnt):
                return {
                    f'result for condition {index}': 'F',
                    'T Num': true_cnt,
                    'F Num': false_cnt,
                    "Unknown Num": unknown_cnt,
                    "T reasons": true_reasons,
                    "F reasons": false_reasons,
                    "Unknown reasons": unknown_reasons
                }
            elif unknown_cnt > max(true_cnt, false_cnt):
                return {
                    f'result for condition {index}': 'Unknown',
                    'T Num': true_cnt,
                    'F Num': false_cnt,
                    "Unknown Num": unknown_cnt,
                    "T reasons": true_reasons,
                    "F reasons": false_reasons,
                    "Unknown reasons": unknown_reasons
                }
            else: judge_cnt += 1

        return {
            f'result for condition {index}': 'Unknown',
            'T Num': true_cnt,
            'F Num': false_cnt,
            "Unknown Num": unknown_cnt,
            "T reasons": true_reasons,
            "F reasons": false_reasons,
            "Unknown reasons": unknown_reasons
        }

    

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

    root_dir = "/home/shuyang/Project/Static-Inspection-bugs/jq-check"
    result_path_base = "/home/shuyang/Project/df_and_uaf/jq-check/uaf"

    static_analysis_result = ""

    with open("/home/shuyang/Project/Static-Inspection-bugs/jq_use-after-free.txt") as f:
        sar_list = f.read()
        sar_list = sar_list.split("\n\n")
        f.close()
    for idx, sar in enumerate(sar_list):
        sar_lines = sar.split('\n')
        ground_truth = sar_lines[0][2]
        file1 = sar_lines[1][15:]
        line1 = sar_lines[2][6:]
        file2 = sar_lines[3][15:]
        line2 = sar_lines[4][6:]
        static_analysis_result += f'''
{idx+1} Use after free warning:
use at {file1}:{line1}
free at {file2}:{line2}
'''

    sawc = StaticAnalysisWarningsConfirmation(
            root_dir=root_dir,
            make_cmd="", 
            static_analysis_result=static_analysis_result,
            database_path="",
            codeql_result_dir="",
            result_path=f"{result_path_base}/result_all.txt"
        )

    result = asyncio.run(sawc.start())
    print(f'Ground truth: {ground_truth}, LLM result: {result}')