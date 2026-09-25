import sys
sys.path.append("src/")

from confirm import confirm_project
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

    warning_files = os.listdir(warning_dir)
    for wf in warning_files:
        with open(os.path.join(warning_dir, wf), "r") as f:
            warning = json.load(f)
            warning_name_list.append(wf.split(".")[0])
            static_analysis_result_list.append(str(warning))
        f.close()

    confirm_project(
        project_dir=project_path, 
        project_name=project, 
        warning_name_list=[],
        static_analysis_result_list=[], 
        res_path=res_path,
        database_path=database_path, 
        try_times=5
    )


if __name__ == "__main__":

    eval_on_LLM4SA_OS_dataset(
        project="RIOT-2020.04",
        project_path="/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/OS-bench/projects-OS/RIOT-2020.04",
        warning_dir="/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/OS-bench/warnings-OS/RIOT-2020.04/cppcheck_output",
        res_path="/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/OS-bench/result-OS/ours/RIOT-2020.04/cppcheck",
        database_path="/home/tcz/Static-Warning-Confirmation/temp"
    )