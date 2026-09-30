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

    warning_files = os.listdir(warning_dir)
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
        max_parallel=5
    )