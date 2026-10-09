from process import StaticAnalysisWarningsConfirmation
import asyncio
from codequery_tools import build_codequery_db
from datetime import datetime
import os
import json
from concurrent.futures import ThreadPoolExecutor

def _append_one_line(path: str, obj: dict):
    """把一条结果以 JSONL 追加写入文件。同步函数，供 to_thread 调用。"""
    line = json.dumps(obj, ensure_ascii=False) + "\n"
    with open(path, "a") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())

async def validate_one_try(
    project_dir: str,
    static_analysis_result: str,
    res_path: str,
    database_path: str,
    t: int,
):
    result_path = os.path.join(res_path, f"try_{t+1}")
    os.makedirs(result_path, exist_ok=True)

    confirmator = StaticAnalysisWarningsConfirmation(
        root_dir=project_dir,
        static_analysis_result=static_analysis_result,
        res_path=result_path,
        database_path=database_path,
    )
    return await confirmator.start()

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
async def validate_without_build_database(
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

    # 在 loop 内部创建信号量
    sem = asyncio.Semaphore(max_parallel)

    async def run_one(t: int):
        async with sem:
            return await validate_one_try(
                project_dir=project_dir,
                static_analysis_result=static_analysis_result,
                res_path=res_path,
                database_path=database_path,
                t=t,
            )

    # 保持顺序：gather 返回顺序与传入顺序一致
    tasks = [run_one(t) for t in range(try_times)]
    outputs = await asyncio.gather(*tasks, return_exceptions=True)

    results = {}
    tokens = {}
    time = {}
    for t, out in enumerate(outputs):
        if isinstance(out, Exception):
            # 原来 future.result() 会抛异常，这里按需处理
            raise out
        result0, token0, time0 = out
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

async def validate_project_async(
    project_dir: str, 
    project_name: str, 
    warning_name_list: list[str],
    static_analysis_result_list: list[str], 
    res_path: str,
    database_path: str, 
    try_times: int,
    max_parallel: int,
    max_parallel_warnings: int,
):

    if len(warning_name_list) != len(static_analysis_result_list):
        raise ValueError("The length of warning_name_list and static_analysis_result_list are not equal")
    
    # 数据库构建是阻塞 IO，放到线程里跑，避免卡住 loop
    build_result = await asyncio.to_thread(
        build_codequery_db,
        project_dir=project_dir,
        db_dir=database_path,
    )

    if build_result == "Fail":
        raise ValueError("Fail to build database")

    statistics_path = os.path.join(res_path, "statistics.jsonl")

    if not os.path.exists(statistics_path):
        with open(statistics_path, "w") as f:
            f.write("")
        f.close()

    sem = asyncio.Semaphore(max_parallel_warnings)
    write_lock = asyncio.Lock()

    async def run_one(idx: int):
        async with sem:

            sar = static_analysis_result_list[idx]
            cur_res_path = os.path.join(res_path, "details", warning_name_list[idx])

            final, results, tokens, time = await validate_without_build_database(
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

            async with write_lock:
                await asyncio.to_thread(
                    _append_one_line, statistics_path, result_json
                )

            return idx, result_json


    tasks = [run_one(idx) for idx in range(len(static_analysis_result_list))]
    outputs = await asyncio.gather(*tasks, return_exceptions=True)

    for out in outputs:
        if isinstance(out, Exception):
            raise out


def validate_project(
    project_dir: str,
    project_name: str,
    warning_name_list: list,
    static_analysis_result_list: list,
    res_path: str,
    database_path: str,
    try_times: int,
    max_parallel: int,
    max_parallel_warnings: int,
):
    """同步入口，内部启动唯一一个 loop"""
    return asyncio.run(
        validate_project_async(
            project_dir=project_dir,
            project_name=project_name,
            warning_name_list=warning_name_list,
            static_analysis_result_list=static_analysis_result_list,
            res_path=res_path,
            database_path=database_path,
            try_times=try_times,
            max_parallel=max_parallel,
            max_parallel_warnings=max_parallel_warnings,
        )
    )