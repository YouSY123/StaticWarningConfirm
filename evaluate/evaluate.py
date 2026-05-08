import sys
import json
import os
sys.path.append("src/")

from confirm import confirm_project

def eval_on_LLM4SA_os_project(
    project_dir: str, 
    static_analysis_dir: str,
    result_dir: str,
    database_path: str,
    all_result_path: str,
    statistics_path: str,
    project_name: str,
    tp_list: list[str]
):
    
    static_analysis_result_list = []
    log_path_list = []
    result_path_list = []
    warning_name_list = []
    
    warning_files = os.listdir(static_analysis_dir)
    warning_files.sort()
    for warning_file in warning_files:
        warning_fp = os.path.join(static_analysis_dir, warning_file)
        with open(warning_fp, "r") as f:
            warning_content = json.load(f)
        f.close()
        warning_name = warning_file.split(".")[0]
        warning_name_list.append(warning_name)
        static_analysis_result_list.append(warning_content)
        log_path_list.append(os.path.join(result_dir, warning_name, "log.txt"))
        result_path_list.append(os.path.join(result_dir, warning_name, "result.txt"))
        if not os.path.exists(os.path.join(result_dir, warning_name)):
            os.makedirs(os.path.join(result_dir, warning_name))

    result_list = confirm_project(
        project_dir=project_dir, 
        static_analysis_result_list=static_analysis_result_list, 
        log_path_list=log_path_list, 
        result_path_list=result_path_list, 
        database_path=database_path, 
        statistics_path=all_result_path,
        project_name=project_name, 
        warning_name_list=warning_name_list
    )

    statistics = {
        "TT": {
            "cnt": 0,
            "warning": []
        },
        "TF": {
            "cnt": 0,
            "warning": []
        },
        "TU": {
            "cnt": 0,
            "warning": []
        },
        "FT": {
            "cnt": 0,
            "warning": []
        },
        "FF": {
            "cnt": 0,
            "warning": []
        },
        "FU": {
            "cnt": 0,
            "warning": []
        },
    }

    for idx, res in enumerate(result_list):
        if res in tp_list:
            if res == "True Positive":
                statistics["TT"]["cnt"] += 1
                statistics["TT"]["warning"].append(warning_name_list[idx])
            elif res == "False Positive":
                statistics["TF"]["cnt"] += 1
                statistics["TF"]["warning"].append(warning_name_list[idx])
            else:
                statistics["TU"]["cnt"] += 1
                statistics["TU"]["warning"].append(warning_name_list[idx])
        else:
            if res == "True Positive":
                statistics["FT"]["cnt"] += 1
                statistics["FT"]["warning"].append(warning_name_list[idx])
            elif res == "False Positive":
                statistics["FF"]["cnt"] += 1
                statistics["FF"]["warning"].append(warning_name_list[idx])
            else:
                statistics["FU"]["cnt"] += 1
                statistics["FU"]["warning"].append(warning_name_list[idx])

    with open(statistics_path, "w") as f:
        json.dump(statistics, f, indent=4)
    f.close()