import sys
sys.path.append("src/")

from main import validate_project
import os
import json

def eval():

    warning_base = "/home/tcz/Static-Warning-Confirmation/RICAN-bench/warnings/formatted-LLM4SA"
    project_base = "/home/tcz/Static-Warning-Confirmation/RICAN-bench/project-ours"
    result_base = "/home/tcz/Static-Warning-Confirmation/result-RICAN/ours"
    database_path = "/home/tcz/Static-Warning-Confirmation/temp"

    warning_dirs = os.listdir(warning_base)
    warning_dirs.sort()
    for warning_dir in warning_dirs:

        # ==========
        if warning_dir != "tmux_double-free": continue 
        print(warning_dir)
        # ==========

        pj = warning_dir.split("_")[0]
        warning_dir_path = os.path.join(warning_base, warning_dir)

        static_analysis_result_list = []
        warning_name_list = []


        warning_files = os.listdir(warning_dir_path)
        warning_files.sort()
        for warning_file in warning_files:

            warning_fp = os.path.join(warning_dir_path, warning_file)

            with open(warning_fp, "r") as f:
                warning = json.load(f)
                warning_name_list.append(warning_file.split(".")[0])
                static_analysis_result_list.append(str(warning))
            f.close()

        os.makedirs(os.path.join(result_base, warning_dir), exist_ok=True)
        
        validate_project(
            project_dir=os.path.join(project_base, f"{pj}-check"), 
            project_name=pj, 
            warning_name_list=warning_name_list,
            static_analysis_result_list=static_analysis_result_list, 
            res_path=os.path.join(result_base, warning_dir),
            database_path=database_path, 
            try_times=5,
            max_parallel=5,
            max_parallel_warnings=1
        )

if __name__ == "__main__":
    eval()