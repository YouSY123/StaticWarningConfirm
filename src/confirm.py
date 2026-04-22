from process import StaticAnalysisWarningsConfirmation
import asyncio
from codequery_tools import build_codequery_db
from datetime import datetime

# confirm one warning in a project
def confirm(
    project_dir: str, 
    static_analysis_result: str, 
    log_path: str, 
    result_path: str, 
    database_path: str
):
    
    build_result = build_codequery_db(
        project_dir=project_dir,
        db_dir=database_path
    )

    if build_result == "Fail":
        return "build database fail"

    confirmator = StaticAnalysisWarningsConfirmation(
        root_dir=project_dir,
        static_analysis_result=static_analysis_result,
        log_path=log_path,
        result_path=result_path, 
        database_path=database_path
    )

    result = asyncio.run(confirmator.start())
    return result[0]

# confirm a list of warnings in a project, with database builded only once
def confirm_project(
    project_dir: str, 
    static_analysis_result_list: list[str], 
    log_path_list: list[str], 
    result_path_list: list[str], 
    database_path: str, 
    statistics_path: str, 
    project_name: str
):
    
    build_result = build_codequery_db(
        project_dir=project_dir,
        db_dir=database_path
    )

    if build_result == "Fail":
        return "build database fail"
    
    with open(statistics_path, "w") as f:
        f.write("")
    f.close()
    
    result_list = []
    
    for idx, static_analysis_result in enumerate(static_analysis_result_list):

        confirmator = StaticAnalysisWarningsConfirmation(
            root_dir=project_dir,
            static_analysis_result=static_analysis_result,
            log_path=log_path_list[idx],
            result_path=result_path_list[idx], 
            database_path=database_path
        )

        result = asyncio.run(confirmator.start())
        result = result[0]
        result_list.append(result)

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        statistic_information = f"[{project_name}] Warning{idx}: {result} [Time: {time}]\n"

        with open(statistics_path, "a") as f:
            f.write(statistic_information)
        f.close()

    return result_list

confirm(
    project_dir="/home/shuyang/Project/Static-Inspection-bugs/tmux-check",
    static_analysis_result=f"Use after free:\nfree at cmd-capture-pane.c:207\nuse at window.c:1318",
    log_path="/home/shuyang/Project/log_test.txt",
    result_path="/home/shuyang/Project/res_test.txt",
    database_path="/home/shuyang/Project/temp"
)