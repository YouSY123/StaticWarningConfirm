from agents import create_condition_analyzer, create_condition_generator, create_condition_judge_checker_agent, create_condition_checker_agent
import asyncio
import json
from copy import deepcopy
from codequery_tools import get_information_of_project
from tools import init_tools, list_files, view_one_file, view_one_function
from fewshot import get_examples_for_condition_analysis


from config import PRINT_LOG
def print_client_log(title:str, content:str, log_path:str):
    if not PRINT_LOG:
        return
    with open(log_path, 'a') as f:
        f.write(f'----------{title}----------\n')
        f.write(f'{content}\n')
        f.write(f'----------End {title}----------\n\n\n')
    f.close()

def write_result(content:str, result_path:str):
    with open(result_path, 'a') as f:
        f.write(content)
    f.close()

class StaticAnalysisWarningsConfirmation:

    def __init__(self, root_dir, static_analysis_result, log_path, result_path, database_path):

        self.root_dir = root_dir
        self.sar = static_analysis_result
        self.log_path = log_path
        self.result_path = result_path

        # initialize tools
        init_tools(root_dir, database_path)

        # initialize files
        from config import PRINT_LOG
        if PRINT_LOG:
            try:
                with open(self.log_path, 'w') as f:
                    f.write('')
                f.close()
            except Exception as e:
                print("Failed to initialize log file.")
                PRINT_LOG = False

        try:
            with open(self.result_path, 'w') as f:
                f.write('')
            f.close()
        except Exception as e:
            print("Failed to initialize result file.")
            exit("Failed to initialize result file.")


    async def generate_conditions(self, input_info:str):
        # create tools for the agent
        from fewshot import get_example

        # create agent
        from config import CONDITION_GENERATE_MAX_TURN

        log_info = ''
        generate_pass = False
        checker_info = ""

        for turn in range(CONDITION_GENERATE_MAX_TURN):

            # generate conditions
            try: 

                condition_generator = create_condition_generator([get_example, list_files, view_one_file, get_information_of_project, view_one_function])

                result = await condition_generator.ainvoke(
                    {"messages": [{"role": "user", "content": input_info + checker_info}]},
                    {"recursion_limit": 50}
                )

            except Exception as e:
                print(e)
                continue

            dialogue = ''
            for message in result["messages"]:
                if hasattr(message, "content"):
                    if str(message.content) != "":
                        dialogue += (str((message.content)).replace("\n", "\\n") + "\n\n")
                if hasattr(message, "tool_calls"):
                    if message.tool_calls != []:
                        dialogue += (str(message.tool_calls) + "\n\n")


            log_info += f"Condition generation try {turn+1}:\n" + dialogue + "\n\n"

            try:

                checker = create_condition_checker_agent()
                checker_prompt = f"Condition generation process and result:\n{dialogue}"

                checker_result = await checker.ainvoke(
                    {"messages": [{"role": "user", "content": checker_prompt}]},
                    {"recursion_limit": 50}
                )

            except Exception as e:
                continue

            
            log_info += f"Checker for condition generation try {turn+1}:\n" + str(checker_result["messages"][-1].content) + "\n\n"

            checker_result_json = self.extract_json(str(checker_result["messages"][-1].content))

            if "check_result" in checker_result_json:
                if checker_result_json['check_result'] == 'Correct':
                    log_info += f"Generation try {turn+1} result: Correct.\n\n"
                    generate_pass = True
                    break
                else:
                    log_info += f"Generation try {turn+1} result: Incorrect.\n\n"
                    if "explanation" in checker_result_json:
                        checker_info = "\n\nYou have generated conditions for some times, but the checker found out that the conditions have something wrong: \n" + checker_result_json['explanation']
                        last_generation = "\n\nThe conditions you generate before:\n" + str(result["messages"][-1].content)
                        checker_info += last_generation


        if PRINT_LOG:
            print_client_log('Condition Generator', log_info, self.log_path)

        if generate_pass:
            try:

                conditions = self.extract_json(str(result["messages"][-1].content))
                write_result(f"Conditions:\n{json.dumps(conditions, indent=4)}", self.result_path)
                
            except Exception as e:

                write_result("Failed to extract conditions as JSON.\n", self.result_path)
                return {"result": "failed"}

            return conditions
        
        else:
            write_result(f"Failed to generate conditions in {CONDITION_GENERATE_MAX_TURN} times.\n", self.result_path)
            return {"result": "failed"}
    

    def extract_json(self, string_info:str):

        if '```json' in string_info:
            parts = string_info.split('```json')
            string_info = parts[-1]
        if '```' in string_info:
            parts = string_info.split('```')
            string_info = parts[0]
        while len(string_info) != 0 and string_info[-1] != "}" : 
            string_info = string_info[:-1]

        try:
            json_info = json.loads(string_info)
            return json_info
        except Exception as e:
            return "Error"
    

    async def judge_conditions(self, json_info, tools:list, index = 0):

        # run condition judging agents for several times
        from config import CONDITION_VOTE_TIMES, CONDITION_JUDGE_MAX_TURN

        judge_cnt = 0

        async def judge_one_time():

            from config import CONDITION_CHECK_MAX_TURN

            log_info = ''

            judge_pass = False

            checker_info = ""

            for judge_try in range(CONDITION_CHECK_MAX_TURN):

                try:

                    condition_analyzer = create_condition_analyzer(tools)

                    result = await condition_analyzer.ainvoke(
                        {"messages": [{"role": "user", "content": json_info + checker_info}, 
                                      {"role": "user", "content": get_examples_for_condition_analysis()}]},
                        {"recursion_limit": 50}
                    )

                except Exception as e:
                    result = {"result": "None", "explanation": ""}
                    return result

                dialogue = ''
                for message in result["messages"]:
                    if hasattr(message, "content"):
                        if str(message.content) != "":
                            dialogue += (str((message.content)).replace("\n", "\\n") + "\n\n")
                    if hasattr(message, "tool_calls"):
                        if message.tool_calls != []:
                            dialogue += (str(message.tool_calls) + "\n\n")


                log_info += f"Judge try {judge_try+1}:\n" + dialogue + "\n\n" 

                result_json = self.extract_json(str(result["messages"][-1].content))
                if result_json == 'Error': 
                    log_info += f"Judge try {judge_try+1} result: JSON format error.\n\n"
                    continue

                try: 

                    checker_prompt = f"Condition confirmation information:\n{json_info}\n\nCondition judgment to be checked:\n{dialogue}"
                    condition_judge_checker = create_condition_judge_checker_agent()
                    checker_result = await condition_judge_checker.ainvoke(
                        {"messages": [{"role": "user", "content": checker_prompt}]},
                        {"recursion_limit": 50}
                    )

                except Exception as e:
                    result = {"result": "None", "explanation": ""}
                    return result

                log_info += f"Checker for try {judge_try+1}:\n" + str(checker_result["messages"][-1].content) + "\n\n"

                checker_result_json = self.extract_json(str(checker_result["messages"][-1].content))
                if "check_result" in checker_result_json:
                    if checker_result_json['check_result'] == 'Correct':
                        judge_pass = True
                        log_info += f"Judge try {judge_try+1} result: Correct.\n\n"
                        break
                    else:
                        log_info += f"Judge try {judge_try+1} result: Incorrect.\n\n"
                        if "explanation" in checker_result_json:
                            checker_info = "\n\nYou have judged conditions for some times, but the checker found out that the judgment has something wrong: \n" + checker_result_json['explanation']

            if PRINT_LOG:
                print_client_log(f'Condition Inspector {index}', log_info, self.log_path)

            if judge_pass:
                return result_json
            else:
                return {"result": "None", "explanation": "Not pass check"}

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

        # get prompt for the first agent to generate the conditions
        generate_prompt ='The result of the static analyzer:\n' + self.sar
        
        # generate and extract the conditions
        from config import CONDITION_GENERATE_RETRY_TIMES
        condition_retry = 1

        while condition_retry <= CONDITION_GENERATE_RETRY_TIMES:
            # generate conditions
            conditions_json = await self.generate_conditions(generate_prompt)
            # check if conditions generate failed
            if "result" in conditions_json:
                if conditions_json["result"] == "failed":
                    condition_retry += 1
                    if condition_retry > CONDITION_GENERATE_RETRY_TIMES:
                        return ["Condition generation failed."]
                    else:
                        write_result(f"Retry\n", self.result_path)
                        continue
            
            # extract the conditions and get prompts for each judging agent
            # check if conditions format is correct
            judger_prompt = []
            if 'Warning information' in conditions_json:
                for w in conditions_json['Warning information']:
                    warning = conditions_json['Warning information'][w]
                    if "Confirmation conditions" in warning:
                        for c in warning["Confirmation conditions"]:
                            confirmation = warning["Confirmation conditions"][c]
                            new_prompt_json = deepcopy(warning)
                            new_prompt_json["Confirmation conditions"] = confirmation
                            new_prompt_json.pop("Explanation")
                            #print(new_prompt_json)
                            judger_prompt.append(json.dumps(new_prompt_json))
                    else:
                        write_result(f"Wrong format of conditions. Retry\n", self.result_path)
                        continue
            else:
                write_result(f"Wrong format of conditions. Retry\n", self.result_path)
                continue

            break
        
        judge_tasks = [self.judge_conditions(json_info, [list_files, view_one_file, get_information_of_project, view_one_function], idx+1) for idx, json_info in enumerate(judger_prompt)]
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

        print_client_log('Results for conditions', f"conditions:\n{str(conditions_json)}\nresults:\n{str(result)}", self.log_path)

        final_results = []
        for c in result:
            condition_result = 'True positive'
            for key, r in c.items():
                if (list(r.values()))[0] == 'F':
                    condition_result = 'False positive'
                    break
            for key, r in c.items():
                if (list(r.values()))[0] == 'Unknown':
                    condition_result = 'Unknown'
                    break
            
            final_results.append(condition_result)
        print_client_log('Final results', str(condition_result), self.log_path)

        write_result(f"\nFinal results: {final_results}\n", self.result_path)
        write_result(f"\nCondition judgment: {json.dumps(result, indent=4)}\n", self.result_path)

        return final_results