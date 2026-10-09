import sys
sys.path.append("src/")

from main import validate_project
import os
import json

def eval_on_LLM4SA_OS_dataset(
    project,
    project_path,
    warning_dir,
    res_path, 
    database_path
):

    static_analysis_result_list = []
    warning_name_list = []

    os.makedirs(res_path, exist_ok=True)

    warning_files = os.listdir(warning_dir)
    warning_files.sort()
    for wf in warning_files:
        with open(os.path.join(warning_dir, wf), "r") as f:
            warning = json.load(f)
            warning_name_list.append(wf.split(".")[0])
            static_analysis_result_list.append(str(warning))
        f.close()

    validate_project(
        project_dir=project_path, 
        project_name=project, 
        warning_name_list=warning_name_list,
        static_analysis_result_list=static_analysis_result_list, 
        res_path=res_path,
        database_path=database_path, 
        try_times=5,
        max_parallel=5,
        max_parallel_warnings=3
    )

def continue_eval_on_LLM4SA_OS_dataset(
    project,
    project_path,
    warning_dir,
    res_path, 
    database_path,
    start
):

    static_analysis_result_list = []
    warning_name_list = []

    os.makedirs(res_path, exist_ok=True)

    cnt = 0

    warning_files = os.listdir(warning_dir)
    warning_files.sort()
    for wf in warning_files:
        cnt += 1
        if cnt < start: continue
        with open(os.path.join(warning_dir, wf), "r") as f:
            warning = json.load(f)
            warning_name_list.append(wf.split(".")[0])
            static_analysis_result_list.append(str(warning))
        f.close()

    validate_project(
        project_dir=project_path, 
        project_name=project, 
        warning_name_list=warning_name_list,
        static_analysis_result_list=static_analysis_result_list, 
        res_path=res_path,
        database_path=database_path, 
        try_times=5,
        max_parallel=5,
        max_parallel_warnings=3
    )

if __name__ == "__main__":

    # continue_eval_on_LLM4SA_OS_dataset(
    #     project="zephyr-v2.1.0",
    #     project_path="/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/OS-bench/projects-OS/zephyr-v2.1.0",
    #     warning_dir="/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/OS-bench/warnings-OS/zephyr-v2.1.0/cppcheck_output",
    #     res_path="/home/tcz/Static-Warning-Confirmation/result-OS/ours/zephyr-v2.1.0/cppcheck", 
    #     database_path="/home/tcz/Static-Warning-Confirmation/temp",
    #     start=69
    # )

    # continue_eval_on_LLM4SA_OS_dataset(
    #     project="zephyr-v2.1.0",
    #     project_path="/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/OS-bench/projects-OS/zephyr-v2.1.0",
    #     warning_dir="/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/OS-bench/warnings-OS/zephyr-v2.1.0/infer_output",
    #     res_path="/home/tcz/Static-Warning-Confirmation/result-OS/ours/zephyr-v2.1.0/infer", 
    #     database_path="/home/tcz/Static-Warning-Confirmation/temp",
    #     start=141
    # )

    eval_on_LLM4SA_OS_dataset(
        project="TencentOS-tiny",
        project_path="/home/shuyang/projects/LLM4SA-bench/OS-bench/projects-OS/TencentOS-tiny",
        warning_dir="/home/shuyang/projects/LLM4SA-bench/OS-bench/warnings-OS/TencentOS-tiny/cppcheck_output",
        res_path="/home/shuyang/projects/result-OS/ours/TencentOS-tiny/cppcheck", 
        database_path="/home/shuyang/projects/temp"
    )