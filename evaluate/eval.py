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

def eval_on_LLM4SA_APP_dataset(tool):

    res_base = "/home/tcz/Static-Warning-Confirmation/result-APP/ours"
    project_base = "/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/APP-bench/projects-ours"
    warning_base = "/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/APP-bench/warnings_filtered"
    database_path = "/home/tcz/Static-Warning-Confirmation/temp"

    pjs = os.listdir(warning_base)
    pjs.sort()
    for project in pjs:

        warning_dir = os.path.join(warning_base, project, tool, f"{tool}_output")
        project_dir = os.path.join(project_base, project)
        res_dir = os.path.join(res_base, project, tool)

        os.makedirs(res_dir, exist_ok=True)

        static_analysis_result_list = []
        warning_name_list = []

        warning_files = os.listdir(warning_dir)
        warning_files.sort()
        for wf in warning_files:
            with open(os.path.join(warning_dir, wf), "r") as f:
                warning = json.load(f)
                warning_name_list.append(wf.split(".")[0])
                static_analysis_result_list.append(str(warning))
            f.close()

        validate_project(
            project_dir=project_dir, 
            project_name=project, 
            warning_name_list=warning_name_list,
            static_analysis_result_list=static_analysis_result_list, 
            res_path=res_dir,
            database_path=database_path, 
            try_times=5,
            max_parallel=5,
            max_parallel_warnings=1
        )


def re_eval_on_APP(tool, re_eval_project, re_eval_warning_list):


    res_base = "/home/tcz/Static-Warning-Confirmation/result-APP/ours"
    project_base = "/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/APP-bench/projects-ours"
    warning_base = "/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/APP-bench/warnings_filtered"
    database_path = "/home/tcz/Static-Warning-Confirmation/temp"

    pjs = os.listdir(warning_base)
    pjs.sort()
    for project in pjs:

        # ====================
        if project != re_eval_project:
            continue
        # ====================

        warning_dir = os.path.join(warning_base, project, tool, f"{tool}_output")
        project_dir = os.path.join(project_base, project)
        res_dir = os.path.join(res_base, project, tool)

        os.makedirs(res_dir, exist_ok=True)

        # ====================
        statistics_file = os.path.join(res_dir, "statistics.jsonl")
        with open(statistics_file, "a") as f:
            f.write("// Sampled warnings:\n")
        # ====================

        static_analysis_result_list = []
        warning_name_list = []

        warning_files = os.listdir(warning_dir)
        warning_files.sort()

        for wf in warning_files:

            # ====================
            warning_name = wf.split(".")[0]
            if warning_name not in re_eval_warning_list:
                continue
            else:
                print(f"retesting:", tool, project, warning_name)
            # ====================

            with open(os.path.join(warning_dir, wf), "r") as f:
                warning = json.load(f)
                warning_name_list.append(wf.split(".")[0])
                static_analysis_result_list.append(str(warning))
            f.close()

        validate_project(
            project_dir=project_dir, 
            project_name=project, 
            warning_name_list=warning_name_list,
            static_analysis_result_list=static_analysis_result_list, 
            res_path=res_dir,
            database_path=database_path, 
            try_times=5,
            max_parallel=5,
            max_parallel_warnings=1
        )


def continue_eval_on_APP(tool, re_eval_project, start):


    res_base = "/home/tcz/Static-Warning-Confirmation/result-APP/ours"
    project_base = "/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/APP-bench/projects-ours"
    warning_base = "/home/tcz/Static-Warning-Confirmation/LLM4SA-bench/APP-bench/warnings_filtered"
    database_path = "/home/tcz/Static-Warning-Confirmation/temp"

    pjs = os.listdir(warning_base)
    pjs.sort()
    for project in pjs:

        # ====================
        if project != re_eval_project:
            continue
        # ====================

        warning_dir = os.path.join(warning_base, project, tool, f"{tool}_output")
        project_dir = os.path.join(project_base, project)
        res_dir = os.path.join(res_base, project, tool)

        os.makedirs(res_dir, exist_ok=True)

        static_analysis_result_list = []
        warning_name_list = []

        warning_files = os.listdir(warning_dir)
        warning_files.sort()

        for wf in warning_files:

            # ====================
            warning_name = wf.split(".")[0]
            idx = int(warning_name.split("_")[1])
            if idx < start:
                continue
            else:
                print(f"continuing: {project} {idx}")
            # else:
            #     print(f"retesting:", tool, project, warning_name)
            # ====================

            with open(os.path.join(warning_dir, wf), "r") as f:
                warning = json.load(f)
                warning_name_list.append(wf.split(".")[0])
                static_analysis_result_list.append(str(warning))
            f.close()

        validate_project(
            project_dir=project_dir, 
            project_name=project, 
            warning_name_list=warning_name_list,
            static_analysis_result_list=static_analysis_result_list, 
            res_path=res_dir,
            database_path=database_path, 
            try_times=5,
            max_parallel=5,
            max_parallel_warnings=1
        )


if __name__ == "__main__":
    
    re_eval_on_APP(
        "cppcheck", 
        "binutils-2.25.1",
        ["Bug_0682_NPD"]
    )