from process import StaticAnalysisWarningsConfirmation
from datetime import datetime
import asyncio
import json

def evaluate_once(root_dir, static_analysis_result, log_path, result_path, project_name, ground_truth:bool, statistics_file):

    sawc = StaticAnalysisWarningsConfirmation(
        root_dir = root_dir,
        static_analysis_result = static_analysis_result, 
        log_path = log_path, 
        result_path = result_path, 
    )

    with open(statistics_file, 'w') as f:
        f.write('')
    f.close()

    with open(statistics_file, 'a') as f:
        result = asyncio.run(sawc.start())
        result = result[0]
        if result == "True positive": 
            if ground_truth == True:
                f.write(f'[{datetime.now()}] {project_name}: Correct. Result: {result}, Ground Truth: True positive\n')
                return True
            else:
                f.write(f'[{datetime.now()}] {project_name}: Incorrect. Result: {result}, Ground Truth: False positive\n')
                return False
        elif result == "False positive":
            if ground_truth == False:
                f.write(f'[{datetime.now()}] {project_name}: Correct. Result: {result}, Ground Truth: False positive\n')
                return True
            else:
                f.write(f'[{datetime.now()}] {project_name}: Incorrect. Result: {result}, Ground Truth: True positive\n')
                return False
        else:
            f.write(f'[{datetime.now()}] {project_name}: Uncertain. Result: {result}, Ground Truth: {"True positive" if ground_truth else "False positive"}\n')
            return None
        

def eval_primevul_dataset():

    with open("../final_data.json", "r") as f:
        dataset = json.load(f)
    f.close()


    print(evaluate_once(
        root_dir="/home/shuyang/Project/Static-Inspection-bugs/file-check", 
        static_analysis_result="Potential double free\nFirst: src/buffer.c:90\nSecond: src/buffer.c:81", 
        log_path="../log.txt", 
        result_path="../result.txt",
        project_name="project", 
        ground_truth=False,
        statistics_file="../statistics.txt"
    ))