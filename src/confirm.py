from process import StaticAnalysisWarningsConfirmation
import asyncio
from codequery_tools import build_codequery_db
from datetime import datetime
import os
import json

# confirm one warning in a project
def confirm(
    project_dir: str, 
    static_analysis_result: str, 
    res_path: str, 
    database_path: str, 
    try_times: int
):
    
    build_result = build_codequery_db(
        project_dir=project_dir,
        db_dir=database_path
    )

    if build_result == "Fail":
        raise ValueError("Fail to build database")

    results = {}
    tokens = {}
    time = {}
    vote = {
        "T": 0,
        "F": 0,
        "U": 0
    }

    for t in range(try_times):

        result_path=os.path.join(res_path, f"try_{t+1}")
        if not os.path.exists(result_path):
            os.makedirs(result_path)

        confirmator = StaticAnalysisWarningsConfirmation(
            root_dir=project_dir,
            static_analysis_result=static_analysis_result,
            res_path=result_path,
            database_path=database_path
        )

        result0, token0, time0 = asyncio.run(confirmator.start())
        results[f"try_{t+1}"] = result0
        tokens[f"try_{t+1}"] = token0
        time[f"try_{t+1}"] = time0

        if result0 == "True positive":
            vote["T"] += 1
        elif result0 == "False positive":
            vote["F"] += 1
        else:
            vote["U"] += 1

        if vote["T"] > try_times/2 :
            final = "True positive"
        elif vote["F"] > try_times/2 :
            final = "False positive"
        else:
            final = "Unknown"

    return final, results, tokens, time


def confirm_without_building_database(
    project_dir: str, 
    static_analysis_result: str, 
    res_path: str, 
    database_path: str, 
    try_times: int
):
    
    # build_result = build_codequery_db(
    #     project_dir=project_dir,
    #     db_dir=database_path
    # )

    # if build_result == "Fail":
    #     return "build database fail"

    results = {}
    tokens = {}
    time = {}
    vote = {
        "T": 0,
        "F": 0,
        "U": 0
    }

    for t in range(try_times):

        result_path=os.path.join(res_path, f"try_{t+1}")
        if not os.path.exists(result_path):
            os.makedirs(result_path)

        confirmator = StaticAnalysisWarningsConfirmation(
            root_dir=project_dir,
            static_analysis_result=static_analysis_result,
            res_path=result_path,
            database_path=database_path
        )

        result0, token0, time0 = asyncio.run(confirmator.start())
        results[f"try_{t+1}"] = result0
        tokens[f"try_{t+1}"] = token0
        time[f"try_{t+1}"] = time0

        if result0 == "True positive":
            vote["T"] += 1
        elif result0 == "False positive":
            vote["F"] += 1
        else:
            vote["U"] += 1

        if vote["T"] > try_times/2 :
            final = "True positive"
        elif vote["F"] > try_times/2 :
            final = "False positive"
        else:
            final = "Unknown"

    return final, results, tokens, time



# confirm a list of warnings in a project, with database builded only once

def confirm_project(
    project_dir: str, 
    project_name: str, 
    warning_name_list: list[str],
    static_analysis_result_list: list[str], 
    res_path: str,
    database_path: str, 
    try_times: int
):

    if len(warning_name_list) != len(static_analysis_result_list):
        raise ValueError("The length of warning_name_list and static_analysis_result_list are not equal")
    
    build_result = build_codequery_db(
        project_dir=project_dir,
        db_dir=database_path
    )

    if build_result == "Fail":
        raise ValueError("Fail to build database")

    statistics_path = os.path.join(res_path, "statistics.jsonl")

    if not os.path.exists(statistics_path):
        with open(statistics_path, "w") as f:
            f.write("")
        f.close()

    with open(statistics_path, "a") as f:

        for idx, sar in enumerate(static_analysis_result_list):

            cur_res_path = os.path.join(res_path, "details", warning_name_list[idx])

            final, results, tokens, time = confirm_without_building_database(
                project_dir=project_dir,
                static_analysis_result=sar,
                res_path=cur_res_path, 
                database_path=database_path,
                try_times=try_times
            )

            result_json = {
                "project": project_name,
                "warning": warning_name_list[idx],
                "final_result": final,
                "try_results": results, 
                "tokens": tokens,
                "time": time
            }

            f.write(json.dumps(result_json, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

    f.close()