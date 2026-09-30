from process import StaticAnalysisWarningsConfirmation
import asyncio
from codequery_tools import build_codequery_db
from datetime import datetime
import os
import json
from concurrent.futures import ThreadPoolExecutor

# validate one warning in a project
def validate(
    project_dir: str, 
    static_analysis_result: str, 
    res_path: str, 
    database_path: str, 
    try_times: int,
    max_parallel: int,
):
    
    build_result = build_codequery_db(
        project_dir=project_dir,
        db_dir=database_path
    )

    if build_result == "Fail":
        raise ValueError("Fail to build database")

    if try_times <= 0:
        raise ValueError("try_times must be greater than 0")

    if max_parallel <= 0:
        raise ValueError("max_parallel must be greater than 0")

    def run_one(t: int):

        result_path=os.path.join(res_path, f"try_{t+1}")
        os.makedirs(result_path, exist_ok=True)

        confirmator = StaticAnalysisWarningsConfirmation(
            root_dir=project_dir,
            static_analysis_result=static_analysis_result,
            res_path=result_path,
            database_path=database_path
        )

        return asyncio.run(confirmator.start())

    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = [
            executor.submit(run_one, t)
            for t in range(try_times)
        ]

        results = {}
        tokens = {}
        time = {}

        for t, future in enumerate(futures):
            result0, token0, time0 = future.result()
            results[f"try_{t+1}"] = result0
            tokens[f"try_{t+1}"] = token0
            time[f"try_{t+1}"] = time0

    vote = {
        "T": 0,
        "F": 0,
        "U": 0
    }

    for result0 in results.values():
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


# validate one warning in a project, without building CodeQuery database
def validate_without_build_database(
    project_dir: str, 
    static_analysis_result: str, 
    res_path: str, 
    database_path: str, 
    try_times: int,
    max_parallel: int,
):
    
    # build_result = build_codequery_db(
    #     project_dir=project_dir,
    #     db_dir=database_path
    # )

    # if build_result == "Fail":
    #     raise ValueError("Fail to build database")

    if try_times <= 0:
        raise ValueError("try_times must be greater than 0")

    if max_parallel <= 0:
        raise ValueError("max_parallel must be greater than 0")

    def run_one(t: int):

        result_path=os.path.join(res_path, f"try_{t+1}")
        os.makedirs(result_path, exist_ok=True)

        confirmator = StaticAnalysisWarningsConfirmation(
            root_dir=project_dir,
            static_analysis_result=static_analysis_result,
            res_path=result_path,
            database_path=database_path
        )

        return asyncio.run(confirmator.start())

    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = [
            executor.submit(run_one, t)
            for t in range(try_times)
        ]

        results = {}
        tokens = {}
        time = {}

        for t, future in enumerate(futures):
            result0, token0, time0 = future.result()
            results[f"try_{t+1}"] = result0
            tokens[f"try_{t+1}"] = token0
            time[f"try_{t+1}"] = time0

    vote = {
        "T": 0,
        "F": 0,
        "U": 0
    }

    for result0 in results.values():
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


# validate a list of warnings in a project, with database builded only once

def validate_project(
    project_dir: str, 
    project_name: str, 
    warning_name_list: list[str],
    static_analysis_result_list: list[str], 
    res_path: str,
    database_path: str, 
    try_times: int,
    max_parallel: int,
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

            final, results, tokens, time = validate_without_build_database(
                project_dir=project_dir,
                static_analysis_result=sar,
                res_path=cur_res_path, 
                database_path=database_path,
                try_times=try_times,
                max_parallel=max_parallel
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